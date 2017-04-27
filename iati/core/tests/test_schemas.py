"""A module containing tests for the library representation of Schemas."""
from lxml import etree
import pytest
import iati.core.codelists
import iati.core.exceptions
import iati.core.schemas
import iati.core.tests.utilities


class TestSchemas(object):
    """A container for tests relating to Schemas"""

    @pytest.fixture
    def schema_initialised(self):
        """Create a very basic Schema.

        Returns:
            iati.core.schemas.Schema: A Schema that has been initialised with basic values.
        """
        schema_name = iati.core.tests.utilities.SCHEMA_NAME_VALID

        return iati.core.schemas.Schema(name=schema_name)

    def test_schema_default_attributes(self):
        """Check a Schema's default attributes are correct"""
        schema = iati.core.schemas.Schema()

        assert schema.name is None

    @pytest.mark.parametrize("invalid_name", iati.core.tests.utilities.find_parameter_by_type(['str', 'none'], False))
    def test_schema_name_instance(self, invalid_name):
        """Check that an Error is raised when attempting to load a Schema that does not exist.

        Todo:
            Check for type errors when the type is incorrect.
        """
        try:
            _ = iati.core.schemas.Schema(invalid_name)
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised, so this point should not be reached
            assert False

    def test_schema_define_from_xsd(self, schema_initialised):
        """Check that a Schema can be generated from an XSD definition."""
        schema = schema_initialised

        assert schema.name == iati.core.tests.utilities.SCHEMA_NAME_VALID
        assert isinstance(schema.codelists, set)
        assert len(schema.codelists) == 0

    def test_schema_unmodified_includes(self, schema_initialised):
        """Check that local elements can be accessed, but imported elements within unmodified Schema includes cannot be accessed.

        lxml does not contain functionality to access elements within imports defined along the lines of:
        `<xsd:include schemaLocation="NAME.xsd" />`

        Todo:
            Simplify asserts
        """
        schema = schema_initialised
        local_element = 'iati-activities'
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
            Add asserts
        """
        schema = schema_initialised
        local_element = 'iati-activities'
        included_element = 'reporting-org'

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        include_location = schema._schema_base_tree.getroot().find(include_location_xpath).attrib['schemaLocation']
        schema._change_include_to_xinclude()
        xi_node = schema._schema_base_tree.getroot().find(xi_location_xpath)
        include_node_after = schema._schema_base_tree.getroot().find(include_location_xpath)

        # check that the new element has been added
        assert isinstance(xi_node, etree._Element)
        assert xi_node.attrib['href'][-len(include_location):] == include_location
        assert xi_node.attrib['parse'] == 'xml'
        # check that the old element has been removed
        assert include_node_after is None

    def test_schema_flattened_includes(self, schema_initialised):
        """Check that includes are flattened correctly.

        In a full flatten of included elements as `<xi:include href="NAME.xsd" parse="xml" />`, there may be nested `schema` elements and other situations that are not permitted.

        This checks that the flattened xsd is valid and that included elements can be accessed.

        Todo:
            Simplify asserts

            assert that the flattened XML is a valid Schema
        """
        schema = schema_initialised
        local_element = 'iati-activities'
        included_element = 'reporting-org'

        include_location_xpath = (iati.core.constants.NAMESPACE + 'include')
        xi_location_xpath = ('{http://www.w3.org/2001/XInclude}include')
        local_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + local_element + '"]')
        included_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + included_element + '"]')

        schema.flatten_includes()

        assert schema._schema_base_tree.getroot().find(include_location_xpath) is None
        assert schema._schema_base_tree.getroot().find(xi_location_xpath) is None
        assert isinstance(schema._schema_base_tree.getroot().find(local_xpath), etree._Element)
        assert isinstance(schema._schema_base_tree.getroot().find(included_xpath), etree._Element)


    def test_schema_codelists_add(self, schema_initialised):
        """Check that it is possible to add Codelists to the Schema."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Codelist to a Schema multiple times."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)
        codelist2 = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist2)

        assert len(schema.codelists) == 1
