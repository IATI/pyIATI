"""A module containing tests for the library representation of Schemas."""
from lxml import etree
import pytest
import iati.core.codelists
import iati.core.default
import iati.core.exceptions
import iati.core.schemas
import iati.core.tests.utilities


def default_activity_schema():
    """Create a very basic acivity schema.

    Returns:
        iati.core.ActivitySchema: An ActivitySchema that has been initialised based on the default IATI Activity Schema.

    """
    schema_name = iati.core.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID

    return iati.core.default.schema(schema_name)


def default_organisation_schema():
    """Create a very basic organisaion schema.

    Returns:
        iati.core.OrganisaionSchema: An OrganisaionSchema that has been initialised based on the default IATI Organisaion Schema.

    """
    schema_name = iati.core.tests.utilities.SCHEMA_ORGANISATION_NAME_VALID

    return iati.core.default.schema(schema_name)


class TestSchemas(object):
    """A container for tests relating to Schemas."""

    @pytest.fixture(params=[
        iati.core.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID,
        iati.core.tests.utilities.SCHEMA_ORGANISATION_NAME_VALID
    ])
    def schemas_initialised(self, request):
        """Create both an ActivitySchema and OrganisaionSchema class.
        For use where both ActivitySchema and OrganisaionSchema must produce the same result.

        Returns:
            iati.core.ActivitySchema / iati.core.OrganisaionSchema: An activity and organisaion that has been initialised based on the default IATI Activity and Organisaion schemas.

        """
        schema_name = request.param

        return iati.core.default.schema(schema_name)

    @pytest.mark.parametrize("schema_type, expected_value", [
        (default_activity_schema, 'iati-activities'),
        (default_organisation_schema, 'iati-organisations')
    ])
    def test_schema_default_attributes(self, schema_type, expected_value):
        """Check a Schema's default attributes are correct."""
        schema = schema_type()

        assert schema.root_element_name == expected_value

    def test_schema_define_from_xsd(self, schemas_initialised):
        """Check that a Schema can be generated from an XSD definition."""
        schema = schemas_initialised

        assert isinstance(schema.codelists, set)
        assert len(schema.codelists) == 0

    @pytest.mark.parametrize("schema_type, expected_local_element", [
        (default_activity_schema, 'iati-activities'),
        (default_organisation_schema, 'iati-organisations')
    ])
    def test_schema_unmodified_includes(self, schema_type, expected_local_element):
        """Check that local elements can be accessed, but imported elements within unmodified Schema includes cannot be accessed.

        lxml does not contain functionality to access elements within imports defined along the lines of:
        `<xsd:include schemaLocation="NAME.xsd" />`

        Todo:
            Simplify asserts.

        """
        schema = schema_type()
        local_element = expected_local_element
        included_element = 'reporting-org'

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        assert schema._schema_base_tree.getroot().find(include_location_xpath).attrib['schemaLocation'] == 'iati-common.xsd'
        assert isinstance(schema._schema_base_tree.getroot().find(local_xpath), etree._Element)
        assert schema._schema_base_tree.getroot().find(included_xpath) is None

    @pytest.mark.parametrize("schema_type, expected_local_element", [
        (default_activity_schema, 'iati-activities'),
        (default_organisation_schema, 'iati-organisations')
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
        schema = schema_type()
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

            Test that this works with subclasses of iati.core.Schema: iati.core.ActivitySchema and iati.core.OrganisationSchema

        """
        schema_path = iati.core.resources.get_schema_path(schema_name)
        schema = iati.core.Schema(schema_path)
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

    def test_schema_codelists_add(self, schemas_initialised):
        """Check that it is possible to add Codelists to the Schema."""
        codelist_name = "a test Codelist name"
        schema = schemas_initialised
        codelist = iati.core.Codelist(codelist_name)

        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_twice(self, schemas_initialised):
        """Check that it is not possible to add the same Codelist to a Schema multiple times."""
        codelist_name = "a test Codelist name"
        schema = schemas_initialised
        codelist = iati.core.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schemas_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema."""
        codelist_name = "a test Codelist name"
        schema = schemas_initialised
        codelist = iati.core.Codelist(codelist_name)
        codelist2 = iati.core.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist2)

        assert len(schema.codelists) == 1

    @pytest.mark.parametrize("schema_type, xsd_element_name, expected_type", [
        (default_activity_schema, 'iati-activities', etree._Element),
        (default_activity_schema, 'iati-activity', etree._Element),
        (default_activity_schema, 'activity-date', etree._Element),
        (default_activity_schema, 'provider-org', etree._Element),  # The 'provider-org' element is deeply nested XSD element.
        (default_activity_schema, 'element-name-that-does-not-exist', type(None)),
        (default_organisation_schema, 'iati-organisations', etree._Element),
        (default_organisation_schema, 'organisation-identifier', etree._Element),  # The 'organisation-identifier' is defined within the 'iati-organisation' element.
        (default_organisation_schema, 'sector', type(None))
    ])
    def test_get_xsd_element(self, schema_type, xsd_element_name, expected_type):
        """Check that an lxml object is returned to represent an XSD element.

        Todo
            Test for elements that should be contained within a flattened schema.
        """
        schema = schema_type()

        result = schema.get_xsd_element(xsd_element_name)

        assert isinstance(result, expected_type)

    @pytest.mark.parametrize("schema_type, xsd_element_name", [
        (default_activity_schema, 'iati-activities'),
        (default_activity_schema, 'contact-info'),
        (default_activity_schema, 'iati-identifier'),  # No child elements
        (default_organisation_schema, 'iati-organisations'),
        (default_organisation_schema, 'total-budget'),
        (default_organisation_schema, 'organisation-identifier')  # No child elements
    ])
    def test_get_child_xsd_elements(self, schema_type, xsd_element_name):
        """Check that a list of lxml objects are returned to represent all child XSD elements. Also check that each item in the result is of the expected type.

        Todo
            Test for elements that should be contained within a flattened schema.
        """
        schema = schema_type()
        parent_element = schema.get_xsd_element(xsd_element_name)

        result = schema.get_child_xsd_elements(parent_element)

        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, etree._Element)
