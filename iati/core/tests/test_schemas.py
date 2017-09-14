"""A module containing tests for the library representation of Schemas."""
from lxml import etree
import pytest
import iati.core.codelists
import iati.core.default
import iati.core.exceptions
import iati.core.resources
import iati.core.schemas
import iati.core.tests.utilities

standard_version_optional = iati.core.tests.utilities.standard_version_optional


class TestSchemas(object):
    """A container for tests relating to Schemas."""

    @pytest.fixture(params=[
        {
            "path_func": iati.core.resources.get_all_activity_schema_paths,
            "schema_class": iati.core.ActivitySchema
        },
        {
            "path_func": iati.core.resources.get_all_org_schema_paths,
            "schema_class": iati.core.OrganisationSchema
        }
    ])
    def schema_initialised(self, request, standard_version_optional):
        """Create and return a single ActivitySchema or OrganisaionSchema object.
        For use where both ActivitySchema and OrganisaionSchema must produce the same result.

        Returns:
            iati.core.Schema: An activity or organisaion Schema that has been initialised.

        """
        schema_path = request.param['path_func'](*standard_version_optional)[0]
        return request.param['schema_class'](schema_path)

    @pytest.mark.parametrize("schema_func, expected_root_element_name", [
        (iati.core.default.activity_schema, 'iati-activities'),
        (iati.core.default.organisation_schema, 'iati-organisations')
    ])
    def test_schema_default_attributes(self, standard_version_optional, schema_func, expected_root_element_name):
        """Check a Schema's default attributes are correct."""
        schema = schema_func(*standard_version_optional)

        assert schema.ROOT_ELEMENT_NAME == expected_root_element_name
        assert expected_root_element_name in schema._source_path

    def test_schema_define_from_xsd(self, schema_initialised):
        """Check that a Schema can be generated from an XSD definition."""
        assert isinstance(schema_initialised.codelists, set)
        assert not schema_initialised.codelists
        assert isinstance(schema_initialised.rulesets, set)
        assert not schema_initialised.rulesets

    @pytest.mark.parametrize("schema_func", [
        iati.core.default.activity_schema,
        iati.core.default.organisation_schema
    ])
    @pytest.mark.parametrize('version', iati.core.constants.STANDARD_VERSIONS)
    def test_schema_get_version(self, schema_func, version):
        """Check that the correct version number is returned by the base classes of iati.core.schemas.schema._get_version()."""
        schema = schema_func(version)
        result = schema._get_version()

        assert result == version

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

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

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

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

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

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        tree = schema.flatten_includes(schema._schema_base_tree)

        assert tree.getroot().find(include_location_xpath) is None
        assert tree.getroot().find(xi_location_xpath) is None
        assert isinstance(tree.getroot().find(local_xpath), etree._Element)
        assert isinstance(tree.getroot().find(included_xpath), etree._Element)
        assert iati.core.utilities.convert_tree_to_schema(tree)

    def test_schema_codelists_add(self, schema_initialised):
        """Check that it is possible to add Codelists to the Schema."""
        codelist_name = "a test Codelist name"
        codelist = iati.core.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)

        assert len(schema_initialised.codelists) == 1

    def test_schema_codelists_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Codelist to a Schema multiple times.

        Todo:
            Consider if this test should test against a versioned Codelist.
        """
        codelist_name = "a test Codelist name"
        codelist = iati.core.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist)

        assert len(schema_initialised.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema.

        Todo:
            Consider if this test should test against a versioned Codelist.
        """
        codelist_name = "a test Codelist name"
        codelist = iati.core.Codelist(codelist_name)
        codelist2 = iati.core.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist2)

        assert len(schema_initialised.codelists) == 1

    def test_schema_rulesets_add(self, schema_initialised):
        """Check that it is possible to add Rulesets to the Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        ruleset = iati.core.Ruleset()

        schema_initialised.rulesets.add(ruleset)

        assert len(schema_initialised.rulesets) == 1

    @pytest.mark.skip(reason='Not implemented')
    def test_schema_rulesets_add_twice(self, schema_initialised):
        """Check that it is not possible to add the sameRulesets to a Schema multiple times.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        raise NotImplementedError

    @pytest.mark.skip(reason='Not implemented')
    def test_schema_rulesets_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Rulesets to a Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.
        """
        raise NotImplementedError
