"""A module containing tests for the library representation of Schemas."""
from lxml import etree
import pytest
import iati.core.codelists
import iati.core.default
import iati.core.exceptions
import iati.core.schemas
import iati.core.tests.utilities


class TestSchemas(object):
    """A container for tests relating to Schemas."""

    @pytest.fixture(params=[
        iati.core.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID,
        iati.core.tests.utilities.SCHEMA_ORGANISATION_NAME_VALID
    ])
    def schema_initialised(self, request):
        """Create and return a single ActivitySchema or OrganisaionSchema object.
        For use where both ActivitySchema and OrganisaionSchema must produce the same result.

        Returns:
            iati.core.ActivitySchema / iati.core.OrganisaionSchema: An activity and organisaion that has been initialised based on the default IATI Activity and Organisaion schemas.

        """
        schema_name = request.param

        return iati.core.default.schema(schema_name)

    @pytest.mark.parametrize("schema_type, expected_root_element_name", [
        ('iati-activities-schema', 'iati-activities'),
        ('iati-organisations-schema', 'iati-organisations')
    ])
    def test_schema_default_attributes(self, schema_type, expected_root_element_name):
        """Check a Schema's default attributes are correct."""
        schema = iati.core.default.schema(schema_type)

        assert schema.ROOT_ELEMENT_NAME == expected_root_element_name
        assert expected_root_element_name in schema._source_path

    def test_schema_define_from_xsd(self, schema_initialised):
        """Check that a Schema can be generated from an XSD definition."""
        assert isinstance(schema_initialised.codelists, set)
        assert not schema_initialised.codelists
        assert isinstance(schema_initialised.rulesets, set)
        assert not schema_initialised.rulesets

    @pytest.mark.parametrize("schema_type, expected_local_element", [
        ('iati-activities-schema', 'iati-activities'),
        ('iati-organisations-schema', 'iati-organisations')
    ])
    def test_schema_unmodified_includes(self, schema_type, expected_local_element):
        """Check that local elements can be accessed, but imported elements within unmodified Schema includes cannot be accessed.

        lxml does not contain functionality to access elements within imports defined along the lines of:
        `<xsd:include schemaLocation="NAME.xsd" />`

        Todo:
            Simplify asserts.

        """
        schema = iati.core.default.schema(schema_type)
        local_element = expected_local_element
        included_element = 'reporting-org'

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        assert schema._schema_base_tree.getroot().find(include_location_xpath).attrib['schemaLocation'] == 'iati-common.xsd'
        assert isinstance(schema._schema_base_tree.getroot().find(local_xpath), etree._Element)
        assert schema._schema_base_tree.getroot().find(included_xpath) is None

    @pytest.mark.parametrize("schema_type, expected_local_element", [
        ('iati-activities-schema', 'iati-activities'),
        ('iati-organisations-schema', 'iati-organisations')
    ])
    def test_schema_modified_includes(self, schema_type, expected_local_element):
        """Check that elements within unflattened modified Schema includes cannot be accessed.

        lxml contains functionality to access elements within imports defined along the lines of:
        `<xi:include href="NAME.xsd" parse="xml" />`
        when there is a namespace defined against the root schema element as `xmlns:xi="http://www.w3.org/2001/XInclude"`

        Todo:
            Simplify asserts.

            Consider consolidating variables shared between multiple tests.

        """
        schema = iati.core.default.schema(schema_type)
        local_element = expected_local_element
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

    @pytest.mark.parametrize("schema_name, expected_local_element", [
        (iati.core.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID, 'iati-activities'),
        (iati.core.tests.utilities.SCHEMA_ORGANISATION_NAME_VALID, 'iati-organisations')
    ])
    def test_schema_flattened_includes(self, schema_name, expected_local_element):
        """Check that includes are flattened correctly.

        In a full flatten of included elements as `<xi:include href="NAME.xsd" parse="xml" />`, there may be nested `schema` elements and other situations that are not permitted.

        This checks that the flattened xsd is valid and that included elements can be accessed.

        Todo:
            Simplify asserts.

            Assert that the flattened XML is a valid Schema.

            Test that this works with subclasses of iati.core.schemas.Schema: iati.core.ActivitySchema and iati.core.OrganisationSchema

        """
        schema_path = iati.core.resources.get_schema_path(schema_name)
        schema = iati.core.schemas.Schema(schema_path)
        local_element = expected_local_element
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
        """Check that it is not possible to add the same Codelist to a Schema multiple times."""
        codelist_name = "a test Codelist name"
        codelist = iati.core.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist)

        assert len(schema_initialised.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema."""
        codelist_name = "a test Codelist name"
        codelist = iati.core.Codelist(codelist_name)
        codelist2 = iati.core.Codelist(codelist_name)

        schema_initialised.codelists.add(codelist)
        schema_initialised.codelists.add(codelist2)

        assert len(schema_initialised.codelists) == 1

    def test_schema_rulesets_add(self, schema_initialised):
        """Check that it is possible to add Rulesets to the Schema."""
        ruleset = iati.core.Ruleset()

        schema_initialised.rulesets.add(ruleset)

        assert len(schema_initialised.rulesets) == 1

    @pytest.mark.skip(reason='Not implemented')
    def test_schema_rulesets_add_twice(self, schema_initialised):
        """Check that it is not possible to add the sameRulesets to a Schema multiple times."""
        raise NotImplementedError

    @pytest.mark.skip(reason='Not implemented')
    def test_schema_rulesets_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Rulesets to a Schema."""
        raise NotImplementedError
