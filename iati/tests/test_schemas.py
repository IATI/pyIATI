"""A module containing tests for the library representation of Schemas."""
# pylint: disable=protected-access
import copy
from lxml import etree
import pytest
import iati.codelists
import iati.default
import iati.exceptions
import iati.resources
import iati.schemas
import iati.tests.utilities


class SchemaTestsBase:
    """A base class for all Schema tests."""

    @pytest.fixture(params=[
        {
            "path_func": iati.resources.get_activity_schema_paths,
            "schema_class": iati.ActivitySchema
        },
        {
            "path_func": iati.resources.get_organisation_schema_paths,
            "schema_class": iati.OrganisationSchema
        }
    ])
    def schema_initialised(self, request, std_ver_minor_mixedinst_valid_fullsupport):
        """Create and return a single ActivitySchema or OrganisationSchema object.

        For use where both ActivitySchema and OrganisationSchema must produce the same result.

        Returns:
            iati.Schema: An activity or organisation Schema that has been initialised.

        """
        schema_path = request.param['path_func'](std_ver_minor_mixedinst_valid_fullsupport)[0]
        return request.param['schema_class'](schema_path)


class TestSchemas(SchemaTestsBase):
    """A container for tests relating to Schemas."""

    @pytest.mark.parametrize("schema_func, expected_root_element_name", [
        (iati.default.activity_schema, 'iati-activities'),
        (iati.default.organisation_schema, 'iati-organisations')
    ])
    def test_schema_default_attributes(self, std_ver_minor_mixedinst_valid_fullsupport, schema_func, expected_root_element_name):
        """Check a Schema's default attributes are correct."""
        schema = schema_func(std_ver_minor_mixedinst_valid_fullsupport)

        assert schema.ROOT_ELEMENT_NAME == expected_root_element_name
        assert expected_root_element_name in schema._source_path

    def test_schema_define_from_xsd(self, schema_initialised):
        """Check that a Schema can be generated from an XSD definition."""
        assert isinstance(schema_initialised.codelists, set)
        assert not schema_initialised.codelists
        assert isinstance(schema_initialised.rulesets, set)
        assert not schema_initialised.rulesets

    @pytest.mark.parametrize("schema_func", [
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_schema_get_version(self, schema_func, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that the correct version number is returned by the base classes of iati.schemas.schema._get_version().

        Todo:
            Determine whether the private function that is accessed should be public.

        """
        version_instance = iati.version._normalise_decimal_version(std_ver_minor_mixedinst_valid_fullsupport)

        schema = schema_func(std_ver_minor_mixedinst_valid_fullsupport)
        result = schema._get_version()

        assert result == version_instance

    def test_schema_unmodified_includes(self, schema_initialised):
        """Check that local elements can be accessed, but imported elements within unmodified Schema includes cannot be accessed.

        lxml does not contain functionality to access elements within imports defined along the lines of:
        `<xsd:include schemaLocation="NAME.xsd" />`

        Todo:
            Simplify asserts.

            Consider consolidating variables shared between multiple tests.

        """
        schema = schema_initialised
        local_element = schema.ROOT_ELEMENT_NAME
        included_element = 'reporting-org'

        include_location_xpath = (iati.constants.NAMESPACE + 'include')
        local_xpath = (iati.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        assert schema._schema_base_tree.getroot().find(include_location_xpath).attrib['schemaLocation'] == 'iati-common.xsd'
        assert isinstance(schema._schema_base_tree.getroot().find(local_xpath), etree._Element)
        assert schema._schema_base_tree.getroot().find(included_xpath) is None

    def test_schema_modified_includes(self, schema_initialised):
        """Check that elements within unflattened modified Schema includes cannot be accessed.

        lxml contains functionality to access elements within imports defined along the lines of:
        `<xi:include href="NAME.xsd" parse="xml" />`
        when there is a namespace defined against the root schema element as `xmlns:xi="http://www.w3.org/2001/XInclude"`

        Todo:
            Simplify asserts.

            Consider consolidating variables shared between multiple tests.

        """
        schema = schema_initialised
        local_element = schema.ROOT_ELEMENT_NAME
        included_element = 'reporting-org'

        include_location_xpath = (iati.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        include_location = schema._schema_base_tree.getroot().find(include_location_xpath).attrib['schemaLocation']
        tree = schema._change_include_to_xinclude(schema._schema_base_tree)
        xi_node = tree.getroot().find(xi_location_xpath)
        include_node_after = tree.getroot().find(include_location_xpath)

        # check that the new element has been added
        assert isinstance(xi_node, etree._Element)
        assert xi_node.attrib['href'][-len(include_location):] == include_location
        assert xi_node.attrib['parse'] == 'xml'
        assert isinstance(tree.getroot().find(local_xpath), etree._Element)
        assert not isinstance(tree.getroot().find(included_xpath), etree._Element)
        # check that the old element has been removed
        assert include_node_after is None

    def test_schema_flattened_includes(self, schema_initialised):
        """Check that includes are flattened correctly.

        In a full flatten of included elements as `<xi:include href="NAME.xsd" parse="xml" />`, there may be nested `schema` elements and other situations that are not permitted.

        This checks that the flattened xsd is valid and that included elements can be accessed.

        Todo:
            Simplify asserts.

            Consider consolidating variables shared between multiple tests.

            Assert that the flattened XML is a valid Schema.

        """
        schema = schema_initialised
        local_element = schema.ROOT_ELEMENT_NAME
        included_element = 'reporting-org'

        include_location_xpath = (iati.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        tree = schema.flatten_includes(schema._schema_base_tree)

        assert tree.getroot().find(include_location_xpath) is None
        assert tree.getroot().find(xi_location_xpath) is None
        assert isinstance(tree.getroot().find(local_xpath), etree._Element)
        assert isinstance(tree.getroot().find(included_xpath), etree._Element)
        assert iati.utilities.convert_tree_to_schema(tree)

    def test_schema_codelists_add(self, schema_initialised):
        """Check that it is possible to add Codelists to the Schema."""
        codelist_name = "a test Codelist name"
        codelist = iati.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)

        assert len(schema_initialised.codelists) == 1

    def test_schema_codelists_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Codelist to a Schema multiple times.

        Todo:
            Consider if this test should test against a versioned Codelist.
        """
        codelist_name = "a test Codelist name"
        codelist = iati.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist)

        assert len(schema_initialised.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema.

        Todo:
            Consider if this test should test against a versioned Codelist.
        """
        codelist_name = "a test Codelist name"
        codelist = iati.Codelist(codelist_name)
        codelist2 = iati.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist2)

        assert len(schema_initialised.codelists) == 1

    @pytest.mark.fixed_to_202
    def test_schema_rulesets_add(self, schema_initialised):
        """Check that it is possible to add Rulesets to the Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        ruleset = iati.default.ruleset('2.02')

        schema_initialised.rulesets.add(ruleset)

        assert len(schema_initialised.rulesets) == 1

    @pytest.mark.fixed_to_202
    def test_schema_rulesets_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Ruleset to a Schema multiple times.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        ruleset = iati.default.ruleset('2.02')

        schema_initialised.rulesets.add(ruleset)
        schema_initialised.rulesets.add(ruleset)

        assert len(schema_initialised.rulesets) == 1

    @pytest.mark.fixed_to_202
    def test_schema_rulesets_add_duplicate(self, schema_initialised):
        """Check that it is possible to add multiple functionally identical Rulesets to a Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        ruleset = iati.default.ruleset('2.02')
        ruleset_copy = copy.deepcopy(ruleset)

        schema_initialised.rulesets.add(ruleset)
        schema_initialised.rulesets.add(ruleset_copy)

        assert len(schema_initialised.rulesets) == 2

    @pytest.mark.fixed_to_202
    def test_schema_rulesets_add_two_different(self, schema_initialised):
        """Check that it is possible to add multiple different Rulesets to a Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        ruleset = iati.default.ruleset('2.02')
        ruleset_copy = copy.deepcopy(ruleset)
        ruleset_copy.rules.pop()

        schema_initialised.rulesets.add(ruleset)
        schema_initialised.rulesets.add(ruleset_copy)

        assert len(schema_initialised.rulesets) == 2


class TestSchemaEquality(SchemaTestsBase):
    """A container for tests relating to Schema equality."""

    @pytest.fixture
    def codelist_empty(self):
        """Return a Codelist with no Codes."""
        return iati.Codelist('')

    @pytest.fixture
    def ruleset_empty(self):
        """Return a Ruleset with no Rules."""
        return iati.Ruleset()

    @pytest.fixture
    def ruleset_non_empty(self):
        """Return a non-empty Ruleset."""
        return iati.Ruleset('{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path"]}]}}}')

    def test_schema_same_object_equal(self, schema_initialised, cmp_func_equal_val):
        """Check that a Schema is deemed to be equal with itself."""
        assert cmp_func_equal_val(schema_initialised, schema_initialised)

    def test_schema_same_diff_object_equal(self, schema_initialised, cmp_func_equal_val):
        """Check that two instances of the same Schema are deemed to be equal."""
        schema_copy = copy.deepcopy(schema_initialised)

        assert cmp_func_equal_val(schema_initialised, schema_copy)

    def test_schema_same_num_codelists_equal(self, schema_initialised, codelist_empty, cmp_func_equal_val):
        """Check that two Schemas with the same non-zero number of Codelists are deemed to be equal."""
        schema_initialised.codelists.add(codelist_empty)
        schema_copy = copy.deepcopy(schema_initialised)

        assert cmp_func_equal_val(schema_initialised, schema_copy)

    def test_schema_diff_num_codelists_not_equal(self, schema_initialised, codelist_empty, cmp_func_different_val):
        """Check that two Schemas with different numbers of Codelists are not deemed to be equal."""
        schema_copy = copy.deepcopy(schema_initialised)
        schema_copy.codelists.add(codelist_empty)

        assert cmp_func_different_val(schema_initialised, schema_copy)

    def test_schema_modified_codelist_not_equal(self, schema_initialised, codelist_empty, cmp_func_different_val):
        """Check that two Schemas with where one Codelist is different are not deemed to be equal."""
        schema_initialised.codelists.add(codelist_empty)
        schema_copy = copy.deepcopy(schema_initialised)

        codelist = schema_copy.codelists.pop()
        codelist.name = codelist.name + 'with a difference'
        schema_copy.codelists.add(codelist)

        assert cmp_func_different_val(schema_initialised, schema_copy)

    def test_schema_same_num_rulesets_equal(self, schema_initialised, ruleset_empty, cmp_func_equal_val):
        """Check that two Schemas with the same non-zero number of Rulesets are deemed to be equal."""
        schema_initialised.rulesets.add(ruleset_empty)
        schema_copy = copy.deepcopy(schema_initialised)

        assert cmp_func_equal_val(schema_initialised, schema_copy)

    def test_schema_multiple_equivalent_rulesets_equal(self, schema_initialised, ruleset_empty, ruleset_non_empty, cmp_func_equal_val):
        """Check that two Schemas each with multiple equivalent Rulesets are deemed equal."""
        schema_initialised.rulesets.add(ruleset_empty)
        schema_initialised.rulesets.add(copy.deepcopy(ruleset_empty))
        schema_initialised.rulesets.add(ruleset_non_empty)
        schema_initialised.rulesets.add(copy.deepcopy(ruleset_non_empty))
        schema_copy = copy.deepcopy(schema_initialised)

        assert cmp_func_equal_val(schema_initialised, schema_copy)

    def test_schema_diff_num_equivalent_rulesets_not_equal(self, schema_initialised, ruleset_empty, ruleset_non_empty, cmp_func_different_val):
        """Check that two Schemas each with varied numbers of equivalent Rulesets are not deemed to be equal.

        Each Schema contains one pair of Rulesets that are the deemed to be equal.
        One Schema contains a second pair of equal Rulesets. The other Schema only contains one of these.
        """
        schema_initialised.rulesets.add(ruleset_empty)
        schema_initialised.rulesets.add(copy.deepcopy(ruleset_empty))
        schema_initialised.rulesets.add(ruleset_non_empty)
        schema_initialised.rulesets.add(copy.deepcopy(ruleset_non_empty))
        schema_copy = copy.deepcopy(schema_initialised)

        schema_copy.rulesets.pop()

        assert cmp_func_different_val(schema_initialised, schema_copy)

    def test_schema_diff_num_rulesets_not_equal(self, schema_initialised, ruleset_empty, cmp_func_different_val):
        """Check that two Schemas with different numbers of Rulesets are not deemed to be equal."""
        schema_copy = copy.deepcopy(schema_initialised)
        schema_copy.rulesets.add(ruleset_empty)

        assert cmp_func_different_val(schema_initialised, schema_copy)

    def test_schema_modified_ruleset_not_equal(self, schema_initialised, ruleset_non_empty, cmp_func_different_val):
        """Check that two Schemas with where one Ruleset is different are not deemed to be equal."""
        schema_initialised.rulesets.add(ruleset_non_empty)
        schema_copy = copy.deepcopy(schema_initialised)

        ruleset = schema_copy.rulesets.pop()
        rule = ruleset.rules.pop()
        rule._name = rule.name + 'with-a-difference'
        ruleset.rules.add(rule)
        schema_copy.rulesets.add(ruleset)

        assert cmp_func_different_val(schema_initialised, schema_copy)
