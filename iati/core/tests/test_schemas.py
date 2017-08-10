"""A module containing tests for the library representation of Schemas."""
from lxml import etree
import pytest
import six
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


class MockSchema(iati.core.schemas.Schema):
    """A MockSchema class representing the mock schema defined in iati.core.tests.utilities.PATH_XSD_NON_IATI."""
    root_element_name = "note"


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

    @pytest.mark.parametrize("schema_name, expected_local_element", [
        (iati.core.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID, 'iati-activities'),
        (iati.core.tests.utilities.SCHEMA_ORGANISATION_NAME_VALID, 'iati-organisations')
    ])
    def test_schema_init_schema_containing_includes(self, schema_name, expected_local_element):
        """For a schema that includes another schema, check that includes are flattened correctly.

        In a full flatten of included elements as `<xi:include href="NAME.xsd" parse="xml" />`, there may be nested `schema` elements and other situations that are not permitted.

        This checks that the flattened xsd is valid and that included elements can be accessed.

        Todo:
            Assert that the flattened XML is a valid Schema.

            Test that this works with subclasses of iati.core.Schema: iati.core.ActivitySchema and iati.core.OrganisationSchema

        """
        schema = iati.core.default.schema(schema_name)

        element_name_in_flattened_schema = 'reporting-org'
        element_in_original_schema = schema.get_xsd_element(expected_local_element)
        element_in_flattened_schema = schema.get_xsd_element(element_name_in_flattened_schema)
        xsd_include_element = schema._schema_base_tree.find(
            'xsd:include', namespaces=iati.core.constants.NSMAP
        )
        xi_include_element = schema._schema_base_tree.find(
            'xi:include', namespaces={'xi': 'http://www.w3.org/2001/XInclude'}
        )
        xsd_schema_element = schema._schema_base_tree.find(
            'xsd:schema', namespaces=iati.core.constants.NSMAP
        )

        assert isinstance(element_in_flattened_schema, etree._Element)
        assert isinstance(element_in_original_schema, etree._Element)
        assert xsd_include_element is None
        assert xi_include_element is None
        assert xsd_schema_element is None

    def test_schema_init_schema_containing_no_includes(self):
        """For a schema that does not includes another schema, test that no flattening takes place.

        This test compares the etree.tostring results of the same input file which is instantiated through:
          i) iati.core.Schema, and
          ii) directly from etree.fromstring.

        """
        schema = MockSchema(iati.core.tests.utilities.PATH_XSD_NON_IATI)
        xsd_bytes = iati.core.resources.load_as_bytes(iati.core.tests.utilities.PATH_XSD_NON_IATI)
        schema_direct_from_file = etree.fromstring(xsd_bytes)

        str_schema = etree.tostring(schema._schema_base_tree)
        str_schema_direct_from_file = etree.tostring(schema_direct_from_file)

        assert str_schema == str_schema_direct_from_file

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
        (default_activity_schema, 'reporting-org', etree._Element),  # The 'reporting-org' element is defined within the 'iati-common.xsd schema'.
        (default_activity_schema, 'element-name-that-does-not-exist', type(None)),
        (default_activity_schema, 'total-budget', type(None)),  # There is no 'total-budget' element within the activity schema.
        (default_organisation_schema, 'iati-organisations', etree._Element),
        (default_organisation_schema, 'organisation-identifier', etree._Element),  # The 'organisation-identifier' is defined within the 'iati-organisation' element.
        (default_organisation_schema, 'reporting-org', etree._Element),  # The 'reporting-org' element is defined within the 'iati-common.xsd schema'.
        (default_organisation_schema, 'sector', type(None))  # There is no 'sector' element within the organisation schema.
    ])
    def test_get_xsd_element(self, schema_type, xsd_element_name, expected_type):
        """Check that an lxml object is returned to represent an XSD element.

        Todo
            Test for elements that should be contained within a flattened schema.
        """
        schema = schema_type()

        result = schema.get_xsd_element(xsd_element_name)

        assert isinstance(result, expected_type)

    @pytest.mark.parametrize("schema_type, xsd_element_name, num_expected_child_elements", [
        (default_activity_schema, 'iati-activities', 1),
        (default_activity_schema, 'contact-info', 8),
        (default_activity_schema, 'title', 1),  # Contains 'narrative', but this is defined within the referenced xsd:complexType
        (default_activity_schema, 'iati-identifier', 0),  # Contains no child elements
        (default_organisation_schema, 'iati-organisations', 1),
        (default_organisation_schema, 'total-budget', 4),
        (default_organisation_schema, 'organisation-identifier', 0)  # Contains no child elements
    ])
    def test_get_child_xsd_elements(self, schema_type, xsd_element_name, num_expected_child_elements):
        """Check that a list of lxml objects are returned to represent all child XSD elements. Also check that each item in the result is of the expected type.

        Todo
            Test for elements that should be contained within a flattened schema.
        """
        schema = schema_type()
        parent_element = schema.get_xsd_element(xsd_element_name)

        result = schema.get_child_xsd_elements(parent_element)

        assert isinstance(result, list)
        assert len(result) == num_expected_child_elements
        for item in result:
            assert isinstance(item, etree._Element)

    @pytest.mark.parametrize("schema_type, xsd_element_name, num_expected_attributes", [
        (default_activity_schema, 'iati-activities', 3),
        (default_activity_schema, 'iati-activity', 6),
        (default_activity_schema, 'narrative', 1),  # Contains the 'xml:lang' attribute defined as an extension to the "xsd:string" type
        (default_activity_schema, 'loan-status', 3),  # Contains the 'currency' and 'value-date' attributes, which are referenced and defined elsewere in the schema.
        (default_activity_schema, 'iati-identifier', 0),  # Contains no attributes
        (default_organisation_schema, 'iati-organisations', 2),
        (default_organisation_schema, 'iati-organisation', 3),
        (default_organisation_schema, 'value', 2),
        (default_organisation_schema, 'organisation-identifier', 0)  # Contains no attributes
    ])
    def test_get_attributes_in_xsd_element(self, schema_type, xsd_element_name, num_expected_attributes):
        """Check that a list of lxml objects are returned to represent the attributes contained within a given XSD element. Also check that each item in the result is of the expected type.

        Todo
            Test for attributes that should be contained within elements that are part of a flattened schema.
        """
        schema = schema_type()
        element = schema.get_xsd_element(xsd_element_name)

        result = schema.get_attributes_in_xsd_element(element)

        assert isinstance(result, list)
        assert len(result) == num_expected_attributes
        for item in result:
            assert isinstance(item, etree._Element)

    def test_get_name_from_xsd_element(self):
        """Test that an expected name is found within a mock xsd:element.

        Todo:
            Move the mock xsd file out of the resources/test_data/202 folder, as it is not version specific.

            Rename the mock xsd file with a .xsd file extension.

            Test for a case where there is no xsd:element/@name.  In which case, test that None is returned.
        """
        schema = MockSchema(iati.core.tests.utilities.PATH_XSD_NON_IATI)
        elements = schema._schema_base_tree.findall(
            '//xsd:element',
            namespaces=iati.core.constants.NSMAP
        )

        element_names = [schema.get_xsd_element_or_attribute_name(element) for element in elements]

        assert element_names[0] == 'note'
        assert element_names[1] == 'to'
        assert element_names[2] == 'from'
        assert element_names[3] == 'heading'
        assert element_names[4] == 'body'

    def test_get_name_from_xsd_attribute(self):
        """Test that an expected name is found within a mock xsd:attribute.

        Todo:
            Move the mock xsd file out of the resources/test_data/202 folder, as it is not version specific.

            Rename the mock xsd file with a .xsd file extension.

            Test for a case where there is no xsd:attribute/@name.  In which case, test that None is returned.
        """
        schema = MockSchema(iati.core.tests.utilities.PATH_XSD_NON_IATI)
        element = schema.get_xsd_element('body')
        attributes = schema.get_attributes_in_xsd_element(element)

        result = schema.get_xsd_element_or_attribute_name(attributes[0])

        assert result == 'lang'

    def test_get_name_from_xsd_attribute_xml_lang(self):
        """Test that the expected name for an `xml:lang` element is returned.

        This test uses the attribute at iati-activities/iati-activity/@xml:lang as the test case.
        """
        schema = iati.core.default.schema('iati-activities-schema')
        element = schema.get_xsd_element('iati-activity')
        attributes = schema.get_attributes_in_xsd_element(element)

        attribute_names = [
            schema.get_xsd_element_or_attribute_name(attribute)
            for attribute in attributes
        ]

        assert 'xml:lang' in attribute_names

    def test_is_attribute_xml_lang(self):
        """Test that the expected result is returned when checking if an input is an 'xml:lang' attribute."""
        schema = iati.core.default.schema('iati-activities-schema')
        element_with_xml_lang_attribute = schema.get_xsd_element('iati-activity')
        attribute_xml_lang = schema.get_attributes_in_xsd_element(
            element_with_xml_lang_attribute
        )[1]
        element_without_xml_lang_attribute = schema.get_xsd_element('activity-scope')
        attribute_not_xml_lang = schema.get_attributes_in_xsd_element(
            element_without_xml_lang_attribute
        )[0]

        result_expected_true = schema.is_attribute_xml_lang(attribute_xml_lang)
        result_expected_false = schema.is_attribute_xml_lang(attribute_not_xml_lang[0])

        assert result_expected_true
        assert not result_expected_false

    def test_build_xsd_lookup_mock_schema(self):
        """Test that an expected lookup dictionary is built and set when instantiating a MockSchema."""
        schema = MockSchema(iati.core.tests.utilities.PATH_XSD_NON_IATI)

        result = schema._xsd_lookup

        assert list(result.keys()) == [
            'note',
            'note/to',
            'note/from',
            'note/heading',
            'note/body',
            'note/body/@lang'
        ]
        for element in result.values():
            assert isinstance(element, etree._Element)

    def test_build_xsd_lookup_activity_schema(self):
        """Test that an expected lookup dictionary is built and set when instantiating an ActivitySchema."""
        schema = iati.core.default.schema('iati-activities-schema')

        result = schema._xsd_lookup

        assert len(result) == 344  # Number of 'fields' in the v2.02 activity standard
        assert 'iati-activities' in result.keys()
        assert 'iati-activities/iati-activity' in result.keys()
        assert 'iati-activities/iati-activity/iati-identifier' in result.keys()
        assert 'iati-activities/iati-activity/sector/@code' in result.keys()
        assert 'iati-activities/iati-activity/result/indicator/period/target/comment/narrative' in result.keys()  # Highest level of nesting in the v2.02 activity standard.
        for element in result.values():
            assert isinstance(element, etree._Element)

    def test_build_xsd_lookup_organisation_schema(self):
        """Test that an expected lookup dictionary is built and set when instantiating OrganisationSchema."""
        schema = iati.core.default.schema('iati-organisations-schema')

        result = schema._xsd_lookup

        assert len(result) == 126  # Number of 'fields' in the v2.02 organisation standard.
        assert 'iati-organisations' in result.keys()
        assert 'iati-organisations/iati-organisation' in result.keys()
        assert 'iati-organisations/iati-organisation/organisation-identifier' in result.keys()
        assert 'iati-organisations/iati-organisation/recipient-org-budget/budget-line/value' in result.keys()
        assert 'iati-organisations/iati-organisation/total-budget/budget-line/value/@currency' in result.keys()  # Highest level of nesting in the v2.02 organisation standard.
        for element in result.values():
            assert isinstance(element, etree._Element)

    def test_get_documentation_string(self):
        """Test that an input element returns the expected documentation string."""
        schema = iati.core.default.schema('iati-activities-schema')
        element = schema.get_xsd_element('iati-activity')

        result = schema.get_xsd_documentation_string(element)

        assert isinstance(result, str)
        assert result == 'Top-level element for a single IATI activity report.'

    def test_get_documentation_string(self, schemas_initialised):
        """Test that all elements/attributes (except @iso-date) return a non-empty documentation string.

        Todo:
            Add function in tests.utilities to generate a set of input parameters based on a regex match against the xpaths in schema._xsd_lookup.
            This would then mean that this test can specifically exclude paths containing `@iso-date` from the input.
        """
        schema = schemas_initialised

        for xpath, element in schema._xsd_lookup.items():
            if '@iso-date' in xpath:
                continue  # There is no formal definition for `@iso-date` attributes in (v2.01 & v2.02) of the IATI Standard
            result = schema.get_xsd_documentation_string(element)
            assert isinstance(result, six.string_types)
            assert len(result) > 1

    @pytest.mark.parametrize("language", ['ar', 'fr', 'es', 'sw', 'not-a-valid-language'])
    def test_get_documentation_string_no_documentation_for_lang(self, language):
        """Test that an input element returns an empty string for documentation that does not exist for an input language."""
        schema = iati.core.default.schema('iati-activities-schema')
        element = schema.get_xsd_element('iati-activity')

        result = schema.get_xsd_documentation_string(element, language=language)

        assert isinstance(result, six.string_types)
        assert result == ''

    def test_get_xsd_input_type_for_element(self, schemas_initialised):
        """Test that an input type is detected for a given element.

        Todo:
            Add function in tests.utilities to generate a set of input parameters based on a regex match against the xpaths in schema._xsd_lookup.
            This would then mean that this test can be split into two: one test for elements, one for attribues.
        """
        schema = schemas_initialised

        for xpath, element in schema._xsd_lookup.items():
            result = schema.get_xsd_input_type_for_element(element)
            assert isinstance(result, six.string_types)
            if xpath.split('/').pop().startswith('@'):
                assert result == 'attribute'
            else:
                assert result == 'element'

    @pytest.mark.parametrize("element", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_get_xsd_input_type_for_element_invalid_input(self, element):
        """Test that an unexpected input type raises the expected error."""
        schema = iati.core.default.schema('iati-activities-schema')

        with pytest.raises(TypeError) as excinfo:
            schema.get_xsd_input_type_for_element(element)

        assert str(excinfo.value) == 'Unexpected input type entered.'

    @pytest.mark.parametrize("schema, xpath, expected_min, expected_max", [
        ('iati-activities-schema', 'iati-activities/iati-activity', 1, 'unbounded'),  # Element occurances are defined by xsd:element/@ref
        ('iati-activities-schema', 'iati-activities/iati-activity/title', 1, 1),  # Element occurances are defined by xsd:element/@name
        ('iati-activities-schema', 'iati-activities/iati-activity/transaction/transaction-type', 1, 1),
        ('iati-activities-schema', 'iati-activities/iati-activity/contact-info/department', 0, 1),
        ('iati-activities-schema', 'iati-activities/iati-activity/@last-updated-datetime', 0, 1),
        ('iati-activities-schema', 'iati-activities/iati-activity/default-tied-status/@code', 1, 1),
        ('iati-activities-schema', 'iati-activities/iati-activity/transaction/value/@currency', 0, 1)  #_Attribute occurances are defined within xsd:complexType name="currencyType"
    ])
    def test_get_occurances_for_xpath_examples(self, schema, xpath, expected_min, expected_max):
        """Test that an expected result is returned for a set of input XPaths."""
        schema = iati.core.default.schema(schema)

        result = schema.get_occurances_for_xpath(xpath)

        assert result['min_occurs'] == expected_min
        assert result['max_occurs'] == expected_max

    def test_get_occurances_for_xpath_all_xpaths(self, schemas_initialised):
        """Test that an expected result type is returned for all Xpaths within a schema."""
        schema = schemas_initialised

        for xpath in schema._xsd_lookup.keys():
            result = schema.get_occurances_for_xpath(xpath)
            assert isinstance(result, dict)
            assert len(result) == 2
            assert isinstance(result['min_occurs'], int)
            assert isinstance(result['max_occurs'], (int, six.string_types))  # max_occurs may return 'unbounded'

    @pytest.mark.parametrize("schema, xpath, expected_parent", [
        ('iati-activities-schema', 'iati-activities', None),
        ('iati-activities-schema', 'iati-activities/iati-activity', 'iati-activities'),
        ('iati-activities-schema', 'iati-activities/iati-activity/activity-date/@iso-date', 'iati-activities/iati-activity/activity-date'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/@last-updated-datetime', 'iati-organisations/iati-organisation'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/organisation-identifier', 'iati-organisations/iati-organisation'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/total-budget/period-end/@iso-date', 'iati-organisations/iati-organisation/total-budget/period-end')
    ])
    def test_get_xsd_parent_element(self, schema, xpath, expected_parent):
        """Test that the expected parent element name is returned for a given schema and xpath."""
        schema = iati.core.default.schema(schema)

        result = schema.get_parent_xpath_for_xpath(xpath)

        assert type(result) == type(expected_parent)
        assert result == expected_parent

    @pytest.mark.parametrize("method_that_raises_valueerror", [
        'get_parent_xpath_for_xpath',
        'get_xpaths_for_child_types'
    ])
    @pytest.mark.parametrize("bad_xpath", [
        'not-a-valid-xpath',
        'iati-organisations/iati-activity/iati-identifier'  # Mix of XPaths within the activity and organsation standards.
    ])
    def test_get_xsd_parent_element_raises_exception(self, schemas_initialised, method_that_raises_valueerror, bad_xpath):
        """Test that an invalid expected parent element name is returned for a given schema and xpath."""
        schema = schemas_initialised
        method_to_run_with_bad_xpath = getattr(schema, method_that_raises_valueerror)

        with pytest.raises(ValueError) as excinfo:
            method_to_run_with_bad_xpath(bad_xpath)

        assert str(excinfo.value) == 'The input XPath is not a valid XPath for this Schema.'

    @pytest.mark.parametrize("schema, xpath, expected_num_child_types, expected_child_xpath", [
        ('iati-activities-schema', 'iati-activities', 4, 'iati-activities/iati-activity'),
        ('iati-activities-schema', 'iati-activities/iati-activity', 39, 'iati-activities/iati-activity/document-link'),
        ('iati-activities-schema', 'iati-activities/iati-activity/activity-date/narrative', 1, 'iati-activities/iati-activity/activity-date/narrative/@xml:lang'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation', 12, 'iati-organisations/iati-organisation/@last-updated-datetime'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/total-budget', 5, 'iati-organisations/iati-organisation/total-budget/value'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/total-budget/period-end', 1, 'iati-organisations/iati-organisation/total-budget/period-end/@iso-date')
    ])
    def test_get_xpaths_for_child_types(self, schema, xpath, expected_num_child_types, expected_child_xpath):
        """Test that the expected child types are returned for a given schema and xpath."""
        schema = iati.core.default.schema(schema)

        result = schema.get_xpaths_for_child_types(xpath)

        assert isinstance(result, list)
        assert len(result) == expected_num_child_types
        assert expected_child_xpath in result

    @pytest.mark.parametrize("schema, xpath", [
        ('iati-activities-schema', 'iati-activities/iati-activity/iati-identifier'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/organisation-identifier')
    ])
    def test_get_xpaths_for_child_types_empty(self, schema, xpath):
        """Test that the no child types are returned for elements which contain no child types."""
        schema = iati.core.default.schema(schema)

        result = schema.get_xpaths_for_child_types(xpath)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.parametrize("schema, xpath", [
        ('iati-activities-schema', 'iati-activities/iati-activity/@last-updated-datetime'),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/document-link/@format')
    ])
    def test_get_xpaths_for_child_types_attribute(self, schema, xpath):
        """Test that the an input XPath referring to an attribute returns the expected type."""
        schema = iati.core.default.schema(schema)

        result = schema.get_xpaths_for_child_types(xpath)

        assert type(result) == type(None)

    @pytest.mark.parametrize("schema, xpath, expected_result", [
        ('iati-activities-schema', 'iati-activities/@version', True),
        ('iati-activities-schema', 'iati-activities/iati-activity/sector', False),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/@default-currency', True),
        ('iati-organisations-schema', 'iati-organisations/iati-organisation/name', False)
    ])
    def test_is_xsd_element_attribute(self, schema, xpath, expected_result):
        """Check whether XML schema element is an attribute."""
        schema = iati.core.default.schema(schema)
        element = schema._xsd_lookup[xpath]

        result = schema.is_xsd_element_attribute(element)

        assert result is expected_result

    @pytest.mark.parametrize("junk_data", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_is_xsd_element_attribute_raises_expected_error(self, junk_data, schemas_initialised):
        """Check that unexpected input type raises the expected error."""

        with pytest.raises(TypeError):
            schemas_initialised.is_xsd_element_attribute(junk_data)

    def test_non_schema_element_raises_error(self, schemas_initialised):
        """Check that a non-schema XML element raises the expected error."""
        dataset = iati.core.resources.load_as_tree(iati.core.resources.get_test_data_path('valid'))
        dataset_element = dataset.find('iati-activity')

        with pytest.raises(ValueError) as execinfo:
            schemas_initialised.is_xsd_element_attribute(dataset_element)

        assert 'but expected attribute or element' in str(execinfo.value)
