"""A module containing tests for the library representation of Schemas."""
# pylint: disable=protected-access
from lxml import etree
import pytest
import six
import iati.codelists
import iati.default
import iati.exceptions
import iati.resources
import iati.schemas
import iati.tests.utilities


def default_activity_schema():
    """Create a very basic acivity schema.

    Returns:
        iati.ActivitySchema: An ActivitySchema that has been initialised based on the default IATI Activity Schema.

    """
    schema_name = iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID

    return iati.default.activity_schema()


def default_organisation_schema():
    """Create a very basic organisaion schema.

    Returns:
        iati.OrganisaionSchema: An OrganisaionSchema that has been initialised based on the default IATI Organisaion Schema.

    """
    return iati.default.organisation_schema()


class MockSchema(iati.schemas.Schema):
    """A MockSchema class representing the mock schema defined in iati.tests.utilities.PATH_XSD_NON_IATI."""
    ROOT_ELEMENT_NAME = "note"


class TestSchemas(object):
    """A container for tests relating to Schemas."""

    @pytest.fixture(params=[
        {
            "path_func": iati.resources.get_all_activity_schema_paths,
            "schema_class": iati.ActivitySchema
        },
        {
            "path_func": iati.resources.get_all_organisation_schema_paths,
            "schema_class": iati.OrganisationSchema
        }
    ])
    def schema_initialised(self, request, standard_version_optional):
        """Create and return a single ActivitySchema or OrganisationSchema object.

        For use where both ActivitySchema and OrganisationSchema must produce the same result.

        Returns:
            iati.Schema: An activity or organisation Schema that has been initialised.

        """
        schema_path = request.param['path_func'](*standard_version_optional)[0]
        return request.param['schema_class'](schema_path)

    @pytest.mark.parametrize("schema_func, expected_ROOT_ELEMENT_NAME", [
        (iati.default.activity_schema, 'iati-activities'),
        (iati.default.organisation_schema, 'iati-organisations')
    ])
    def test_schema_default_attributes(self, standard_version_optional, schema_func, expected_ROOT_ELEMENT_NAME):
        """Check a Schema's default attributes are correct."""
        schema = schema_func(*standard_version_optional)

        assert schema.ROOT_ELEMENT_NAME == expected_ROOT_ELEMENT_NAME
        assert expected_ROOT_ELEMENT_NAME in schema._source_path

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
    @pytest.mark.parametrize('version', iati.constants.STANDARD_VERSIONS)
    def test_schema_get_version(self, schema_func, version):
        """Check that the correct version number is returned by the base classes of iati.schemas.schema._get_version()."""
        schema = schema_func(version)
        result = schema._get_version()

        assert result == version

    @pytest.mark.parametrize("schema, expected_local_element", [
        ('activity_schema', 'iati-activities'),
        ('organisation_schema', 'iati-organisations')
    ])
    def test_schema_init_schema_containing_includes(self, schema, expected_local_element):
        """For a schema that includes another schema, check that includes are flattened correctly.

        In a full flatten of included elements as `<xi:include href="NAME.xsd" parse="xml" />`, there may be nested `schema` elements and other situations that are not permitted.

        This checks that the flattened xsd is valid and that included elements can be accessed.

        Todo:
            Assert that the flattened XML is a valid Schema.

            Test that this works with subclasses of iati.Schema: iati.ActivitySchema and iati.OrganisationSchema

        """
        schema = getattr(iati.default, schema)()

        element_name_in_flattened_schema = 'reporting-org'
        element_in_original_schema = schema.get_xsd_element(expected_local_element)
        element_in_flattened_schema = schema.get_xsd_element(element_name_in_flattened_schema)
        xsd_include_element = schema._schema_base_tree.find(
            'xsd:include', namespaces=iati.constants.NSMAP
        )
        xi_include_element = schema._schema_base_tree.find(
            'xi:include', namespaces={'xi': 'http://www.w3.org/2001/XInclude'}
        )
        xsd_schema_element = schema._schema_base_tree.find(
            'xsd:schema', namespaces=iati.constants.NSMAP
        )

        assert isinstance(element_in_flattened_schema, etree._Element)
        assert isinstance(element_in_original_schema, etree._Element)
        assert xsd_include_element is None
        assert xi_include_element is None
        assert xsd_schema_element is None

    def test_schema_init_schema_containing_no_includes(self):
        """For a schema that does not includes another schema, test that no flattening takes place.

        This test compares the etree.tostring results of the same input file which is instantiated through:
          i) iati.Schema, and
          ii) directly from etree.fromstring.

        """
        schema = MockSchema(iati.tests.utilities.PATH_XSD_NON_IATI)
        xsd_bytes = iati.resources.load_as_bytes(iati.tests.utilities.PATH_XSD_NON_IATI)
        schema_direct_from_file = etree.fromstring(xsd_bytes)

        str_schema = etree.tostring(schema._schema_base_tree)
        str_schema_direct_from_file = etree.tostring(schema_direct_from_file)

        assert str_schema == str_schema_direct_from_file

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

    def test_schema_rulesets_add(self, schema_initialised):
        """Check that it is possible to add Rulesets to the Schema.

        Todo:
            Consider if this test should test against a versioned Ruleset.

        """
        ruleset = iati.default.ruleset()

        schema_initialised.rulesets.add(ruleset)

        assert len(schema_initialised.rulesets) == 1

    @pytest.mark.skip(reason='Not implemented')
    def test_schema_rulesets_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Rulesets to a Schema multiple times.

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
        schema = MockSchema(iati.tests.utilities.PATH_XSD_NON_IATI)
        elements = schema._schema_base_tree.findall(
            '//xsd:element',
            namespaces=iati.constants.NSMAP
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
        schema = MockSchema(iati.tests.utilities.PATH_XSD_NON_IATI)
        element = schema.get_xsd_element('body')
        attributes = schema.get_attributes_in_xsd_element(element)

        result = schema.get_xsd_element_or_attribute_name(attributes[0])

        assert result == 'lang'

    def test_get_name_from_xsd_attribute_xml_lang(self):
        """Test that the expected name for an `xml:lang` element is returned.

        This test uses the attribute at iati-activities/iati-activity/@xml:lang as the test case.
        """
        schema = iati.default.activity_schema()
        element = schema.get_xsd_element('iati-activity')
        attributes = schema.get_attributes_in_xsd_element(element)

        attribute_names = [
            schema.get_xsd_element_or_attribute_name(attribute)
            for attribute in attributes
        ]

        assert 'xml:lang' in attribute_names

    def test_is_attribute_xml_lang(self):
        """Test that the expected result is returned when checking if an input is an 'xml:lang' attribute."""
        schema = iati.default.activity_schema()
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
        schema = MockSchema(iati.tests.utilities.PATH_XSD_NON_IATI)

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
        schema = iati.default.activity_schema()

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
        schema = iati.default.organisation_schema()

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
        schema = iati.default.schema('iati-activities-schema')
        element = schema.get_xsd_element('iati-activity')

        result = schema.get_xsd_documentation_string(element)

        assert isinstance(result, str)
        assert result == 'Top-level element for a single IATI activity report.'

    def test_get_documentation_string(self, schema_initialised):
        """Test that all elements/attributes (except @iso-date) return a non-empty documentation string.

        Todo:
            Add function in tests.utilities to generate a set of input parameters based on a regex match against the xpaths in schema._xsd_lookup.
            This would then mean that this test can specifically exclude paths containing `@iso-date` from the input.
        """
        schema = schema_initialised

        for xpath, element in schema._xsd_lookup.items():
            if '@iso-date' in xpath:
                continue  # There is no formal definition for `@iso-date` attributes in (v2.01 & v2.02) of the IATI Standard
            result = schema.get_xsd_documentation_string(element)
            assert isinstance(result, six.string_types)
            assert len(result) > 1

    @pytest.mark.parametrize("language", ['ar', 'fr', 'es', 'sw', 'not-a-valid-language'])
    def test_get_documentation_string_no_documentation_for_lang(self, language):
        """Test that an input element returns an empty string for documentation that does not exist for an input language."""
        schema = iati.default.activity_schema()
        element = schema.get_xsd_element('iati-activity')

        result = schema.get_xsd_documentation_string(element, language=language)

        assert isinstance(result, six.string_types)
        assert result == ''

    def test_get_xsd_input_type_for_element(self, schema_initialised):
        """Test that an input type is detected for a given element.

        Todo:
            Add function in tests.utilities to generate a set of input parameters based on a regex match against the xpaths in schema._xsd_lookup.
            This would then mean that this test can be split into two: one test for elements, one for attribues.
        """
        schema = schema_initialised

        for xpath, element in schema._xsd_lookup.items():
            result = schema.get_xsd_input_type_for_element(element)
            assert isinstance(result, six.string_types)
            if xpath.split('/').pop().startswith('@'):
                assert result == 'attribute'
            else:
                assert result == 'element'

    @pytest.mark.parametrize("element", iati.tests.utilities.generate_test_types([], False))
    def test_get_xsd_input_type_for_element_invalid_input(self, element):
        """Test that an unexpected input type raises the expected error."""
        schema = iati.default.schema('iati-activities-schema')

        with pytest.raises(TypeError) as excinfo:
            schema.get_xsd_input_type_for_element(element)

        assert str(excinfo.value) == 'Unexpected input type entered.'

    @pytest.mark.parametrize("xpath, expected_min, expected_max", [
        ('iati-activities/iati-activity', 1, 'unbounded'),  # Element occurances are defined by xsd:element/@ref
        ('iati-activities/iati-activity/title', 1, 1),  # Element occurances are defined by xsd:element/@name
        ('iati-activities/iati-activity/transaction/transaction-type', 1, 1),
        ('iati-activities/iati-activity/contact-info/department', 0, 1),
        ('iati-activities/iati-activity/@last-updated-datetime', 0, 1),
        ('iati-activities/iati-activity/default-tied-status/@code', 1, 1),
        ('iati-activities/iati-activity/transaction/value/@currency', 0, 1)  #_Attribute occurances are defined within xsd:complexType name="currencyType"
    ])
    def test_get_occurances_for_xpath_examples(self, xpath, expected_min, expected_max):
        """Test that an expected result is returned for a set of input XPaths."""
        schema = iati.default.activity_schema()

        result = schema.get_occurances_for_xpath(xpath)

        assert result['min_occurs'] == expected_min
        assert result['max_occurs'] == expected_max

    def test_get_occurances_for_xpath_all_xpaths(self, schema_initialised):
        """Test that an expected result type is returned for all Xpaths within a schema."""
        schema = schema_initialised

        for xpath in schema._xsd_lookup.keys():
            result = schema.get_occurances_for_xpath(xpath)
            assert isinstance(result, dict)
            assert len(result) == 2
            assert isinstance(result['min_occurs'], int)
            assert isinstance(result['max_occurs'], (int, six.string_types))  # max_occurs may return 'unbounded'

    @pytest.mark.parametrize("schema, xpath, expected_parent", [
        ('activity_schema', 'iati-activities', None),
        ('activity_schema', 'iati-activities/iati-activity', 'iati-activities'),
        ('activity_schema', 'iati-activities/iati-activity/activity-date/@iso-date', 'iati-activities/iati-activity/activity-date'),
        ('organisation_schema', 'iati-organisations/iati-organisation/@last-updated-datetime', 'iati-organisations/iati-organisation'),
        ('organisation_schema', 'iati-organisations/iati-organisation/organisation-identifier', 'iati-organisations/iati-organisation'),
        ('organisation_schema', 'iati-organisations/iati-organisation/total-budget/period-end/@iso-date', 'iati-organisations/iati-organisation/total-budget/period-end')
    ])
    def test_get_xsd_parent_element(self, schema, xpath, expected_parent):
        """Test that the expected parent element name is returned for a given schema and xpath."""
        schema = getattr(iati.default, schema)()

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
    def test_get_xsd_parent_element_raises_exception(self, schema_initialised, method_that_raises_valueerror, bad_xpath):
        """Test that an invalid expected parent element name is returned for a given schema and xpath."""
        schema = schema_initialised
        method_to_run_with_bad_xpath = getattr(schema, method_that_raises_valueerror)

        with pytest.raises(ValueError) as excinfo:
            method_to_run_with_bad_xpath(bad_xpath)

        assert str(excinfo.value) == 'The input XPath is not a valid XPath for this Schema.'

    @pytest.mark.parametrize("schema, xpath, expected_num_child_types, expected_child_xpath", [
        ('activity_schema', 'iati-activities', 4, 'iati-activities/iati-activity'),
        ('activity_schema', 'iati-activities/iati-activity', 39, 'iati-activities/iati-activity/document-link'),
        ('activity_schema', 'iati-activities/iati-activity/activity-date/narrative', 1, 'iati-activities/iati-activity/activity-date/narrative/@xml:lang'),
        ('organisation_schema', 'iati-organisations/iati-organisation', 12, 'iati-organisations/iati-organisation/@last-updated-datetime'),
        ('organisation_schema', 'iati-organisations/iati-organisation/total-budget', 5, 'iati-organisations/iati-organisation/total-budget/value'),
        ('organisation_schema', 'iati-organisations/iati-organisation/total-budget/period-end', 1, 'iati-organisations/iati-organisation/total-budget/period-end/@iso-date')
    ])
    def test_get_xpaths_for_child_types(self, schema, xpath, expected_num_child_types, expected_child_xpath):
        """Test that the expected child types are returned for a given schema and xpath."""
        schema = getattr(iati.default, schema)()

        result = schema.get_xpaths_for_child_types(xpath)

        assert isinstance(result, list)
        assert len(result) == expected_num_child_types
        assert expected_child_xpath in result

    @pytest.mark.parametrize("schema, xpath", [
        ('activity_schema', 'iati-activities/iati-activity/iati-identifier'),
        ('organisation_schema', 'iati-organisations/iati-organisation/organisation-identifier')
    ])
    def test_get_xpaths_for_child_types_empty(self, schema, xpath):
        """Test that the no child types are returned for elements which contain no child types."""
        schema = getattr(iati.default, schema)()

        result = schema.get_xpaths_for_child_types(xpath)

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.parametrize("schema, xpath", [
        ('activity_schema', 'iati-activities/iati-activity/@last-updated-datetime'),
        ('organisation_schema', 'iati-organisations/iati-organisation/document-link/@format')
    ])
    def test_get_xpaths_for_child_types_attribute(self, schema, xpath):
        """Test that the an input XPath referring to an attribute returns the expected type."""
        schema = getattr(iati.default, schema)()

        result = schema.get_xpaths_for_child_types(xpath)

        assert type(result) == type(None)

    @pytest.mark.parametrize("schema, xpath, expected_result", [
        ('activity_schema', 'iati-activities/@version', True),
        ('activity_schema', 'iati-activities/iati-activity/sector', False),
        ('organisation_schema', 'iati-organisations/iati-organisation/@default-currency', True),
        ('organisation_schema', 'iati-organisations/iati-organisation/name', False)
    ])
    def test_is_xsd_element_attribute(self, schema, xpath, expected_result):
        """Check whether XML schema element is an attribute."""
        schema = getattr(iati.default, schema)()
        element = schema._xsd_lookup[xpath]

        result = schema.is_xsd_element_attribute(element)

        assert result is expected_result

    @pytest.mark.parametrize("junk_data", iati.tests.utilities.generate_test_types([], False))
    def test_is_xsd_element_attribute_raises_expected_error(self, junk_data, schema_initialised):
        """Check that unexpected input type raises the expected error."""

        with pytest.raises(TypeError):
            schema_initialised.is_xsd_element_attribute(junk_data)

    def test_non_schema_element_raises_error(self, schema_initialised):
        """Check that a non-schema XML element raises the expected error."""
        dataset = iati.resources.load_as_tree(iati.resources.get_test_data_path('valid'))
        dataset_element = dataset.find('iati-activity')

        with pytest.raises(ValueError) as execinfo:
            schema_initialised.is_xsd_element_attribute(dataset_element)

        assert 'but expected attribute or element' in str(execinfo.value)

    @pytest.mark.parametrize("schema, xpath, same_type, expected_num_siblings, expected_sibling_xpath", [
        ('activity_schema', 'iati-activities/iati-activity/sector', True, 32, 'iati-activities/iati-activity/document-link'),
        ('activity_schema', 'iati-activities/iati-activity/sector', False, 38, 'iati-activities/iati-activity/@default-currency'),
        ('activity_schema', 'iati-activities/iati-activity/result/indicator/period/target', True, 3, 'iati-activities/iati-activity/result/indicator/period/actual'),
        ('organisation_schema', 'iati-organisations/iati-organisation/total-budget/value', True, 3, 'iati-organisations/iati-organisation/total-budget/budget-line'),
        ('organisation_schema', 'iati-organisations/iati-organisation/total-budget/value', False, 4, 'iati-organisations/iati-organisation/total-budget/@status'),
        ('organisation_schema', 'iati-organisations/iati-organisation/recipient-region-budget/recipient-region', False, 5, 'iati-organisations/iati-organisation/recipient-region-budget/@status')
    ])
    def test_get_xpaths_for_sibling_types(self, schema, xpath, same_type, expected_num_siblings, expected_sibling_xpath):
        """Test that an expected number of siblings are found for given input XPath."""
        schema = getattr(iati.default, schema)()

        result = schema.get_xpaths_for_sibling_types(xpath, same_type)

        assert isinstance(result, list)
        assert len(result) == expected_num_siblings
        assert expected_sibling_xpath in result

    def test_get_xpaths_for_sibling_types_root_element(self, schema_initialised):
        """Test that no siblings are found for the root element of a Schema."""
        root_element_xpath = schema_initialised.ROOT_ELEMENT_NAME

        result = schema_initialised.get_xpaths_for_sibling_types(root_element_xpath)

        assert result == []

    def test_get_documentation_for_xpath_structure(self, schema_initialised):
        """Test that an expected structure is returned when calling iati.schemas.get_documentation_for_xpath."""
        result = schema_initialised.get_documentation_for_xpath(schema_initialised.ROOT_ELEMENT_NAME)

        assert isinstance(result, dict)
        assert len(result) == 6
        assert 'documentation' in result.keys()
        assert 'input_type' in result.keys()
        assert 'occurances' in result.keys()
        assert 'parent_xpath' in result.keys()
        assert 'sibling_xpaths' in result.keys()
        assert 'child_xpaths' in result.keys()

    def test_get_documentation_for_xpath_content(self):
        """Test that an expected content is returned when calling iati.schemas.get_documentation_for_xpath on a known XPath."""
        schema = iati.default.activity_schema()
        xpath = 'iati-activities/iati-activity/title/narrative'

        result = schema.get_documentation_for_xpath(xpath)

        assert result == {
            'child_xpaths': ['iati-activities/iati-activity/title/narrative/@xml:lang'],
            'documentation': 'The free text name or description of the item being described. This can be repeated in multiple languages.',
            'input_type': 'element',
            'occurances': {'max_occurs': 'unbounded', 'min_occurs': 1},
            'parent_xpath': 'iati-activities/iati-activity/title',
            'sibling_xpaths': []
        }

    def test_get_documentation_for_xpath_raises_exception(self, schema_initialised):
        """Test that iati.schemas.get_documentation_for_xpath raises an exception when passing an invalid XPath."""
        xpath = 'not-a-valid-xpath'

        with pytest.raises(ValueError) as execinfo:
            schema_initialised.get_documentation_for_xpath(xpath)

        assert str(execinfo.value) == 'The input xpath ({0}) is not valid for this schema.'.format(xpath)
