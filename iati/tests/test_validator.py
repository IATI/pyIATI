"""A module containing tests for data validation."""
import pytest
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
import iati.validator


class TestValidationError(object):
    """A container for tests relating to ValidationErrors."""

    def test_validation_error_init_no_name(self):
        """Test that a ValidationError cannot be created with no name provided."""
        with pytest.raises(TypeError):
            iati.validator.ValidationError()

    @pytest.mark.parametrize("invalid_err_name", iati.core.tests.utilities.generate_test_types([], True))
    def test_validation_error_init_bad_name_type(self, invalid_err_name):
        """Test that a ValidationError cannot be created with a name that does not exist."""
        with pytest.raises(ValueError):
            iati.validator.ValidationError(invalid_err_name)

    def test_error_log_init_valid_name(self):
        """Test that a ValidationError can be created when provided a valid name."""
        err_name = 'err-code-not-on-codelist'
        err = iati.validator.ValidationError(err_name)
        err_detail = iati.validator.get_error_codes()[err_name]

        assert isinstance(err, iati.validator.ValidationError)
        assert err.name == err_name
        assert err.base_exception == ValueError
        assert err.category == err_detail['category']
        assert err.description == err_detail['description']
        assert err.info == err_detail['info']
        assert err.help == err_detail['help']


class TestValidationErrorLog(object):
    """A container for tests relating to Validation Error Logs."""

    @pytest.fixture
    def err_name(self):
        """The name of an error."""
        return 'err-code-not-on-codelist'

    @pytest.fixture
    def err_type(self, err_name):
        """The type of an error."""
        return iati.validator.get_error_codes()[err_name]['base_exception']

    @pytest.fixture
    def error(self, err_name):
        """An error."""
        return iati.validator.ValidationError(err_name)

    @pytest.fixture
    def warning_name(self):
        """The name of a warning."""
        return 'warn-code-not-on-codelist'

    @pytest.fixture
    def warning_type(self, warning_name):
        """The type of an error."""
        return iati.validator.get_error_codes()[warning_name]['base_exception']

    @pytest.fixture
    def unused_exception_type(self):
        """An exception type that is not covered by the ValidationErrors."""
        return MemoryError

    @pytest.fixture
    def warning(self, warning_name):
        """A warning."""
        return iati.validator.ValidationError(warning_name)

    @pytest.fixture
    def error_log(self):
        """A basic error log that is initially empty."""
        return iati.validator.ValidationErrorLog()

    @pytest.fixture
    def error_log_with_error(self, error):
        """An error log with an error added."""
        error_log = iati.validator.ValidationErrorLog()
        error_log.add(error)

        return error_log

    @pytest.fixture
    def error_log_with_warning(self, warning):
        """An error log with a warning added."""
        error_log = iati.validator.ValidationErrorLog()
        error_log.add(warning)

        return error_log

    @pytest.fixture
    def error_log_mixed_contents(self, error, warning):
        """An error log with both an error and a warning added."""
        error_log = iati.validator.ValidationErrorLog()
        error_log.add(error)
        error_log.add(warning)

        return error_log

    def test_error_log_init(self, error_log):
        """Test that a validator ErrorLog can be created and acts as a set."""
        assert isinstance(error_log, iati.validator.ValidationErrorLog)
        assert len(error_log) == 0
        assert not error_log.contains_errors()
        assert not error_log.contains_warnings()

    def test_error_log_add_errors(self, error_log_with_error, err_name, warning_name, err_type):
        """Test that errors are identified as errors when added to the error log."""
        assert len(error_log_with_error) == 1
        assert error_log_with_error.contains_errors()
        assert not error_log_with_error.contains_warnings()
        assert error_log_with_error.contains_error_called(err_name)
        assert not error_log_with_error.contains_error_called(warning_name)
        assert error_log_with_error.contains_error_of_type(err_type)

    def test_error_log_add_warnings(self, error_log_with_warning, err_name, warning_name, warning_type):
        """Test that warnings are not identified as errors when added to the error log."""
        assert len(error_log_with_warning) == 1
        assert not error_log_with_warning.contains_errors()
        assert error_log_with_warning.contains_warnings()
        assert not error_log_with_warning.contains_error_called(err_name)
        assert error_log_with_warning.contains_error_called(warning_name)
        assert error_log_with_warning.contains_error_of_type(warning_type)

    def test_error_log_add_mixed(self, error_log_mixed_contents, err_name, warning_name, err_type, warning_type, unused_exception_type):
        """Test that a mix of errors and warnings are identified as such when added to the error log."""
        assert len(error_log_mixed_contents) == 2
        assert error_log_mixed_contents.contains_errors()
        assert error_log_mixed_contents.contains_warnings()
        assert error_log_mixed_contents.contains_error_called(err_name)
        assert error_log_mixed_contents.contains_error_called(warning_name)
        assert error_log_mixed_contents.contains_error_of_type(err_type)
        assert error_log_mixed_contents.contains_error_of_type(warning_type)
        assert not error_log_mixed_contents.contains_error_of_type(unused_exception_type)

    @pytest.mark.parametrize("not_ValidationError", iati.core.tests.utilities.generate_test_types([], True))
    def test_error_log_add_incorrect_type(self, error_log, not_ValidationError):
        """Test that you may only add ValidationErrors to a ValidationErrorLog."""
        with pytest.raises(TypeError):
            error_log.add(not_ValidationError)

    @pytest.mark.parametrize("potential_ValidationError", iati.core.tests.utilities.generate_test_types([], True) + [iati.validator.ValidationError('err-code-not-on-codelist')])
    def test_error_log_set_index_incorrect_type(self, error_log_with_warning, potential_ValidationError):
        """Test that you may not add values to an error log via index assignment."""
        with pytest.raises(TypeError):
            error_log_with_warning[0] = potential_ValidationError

    def test_error_log_equality_single_error(self, error_log_with_error, error_log_with_warning):
        """Test equality between a pair of ValidationErrorLogs.

        Each error log contains the same number of errors. Each has different errors.
        """
        assert not error_log_with_error == error_log_with_warning
        assert not error_log_with_warning == error_log_with_error
        assert error_log_with_error != error_log_with_warning
        assert error_log_with_warning != error_log_with_error

    def test_error_log_equality_extended_log(self, error_log, error_log_with_error):
        """Test equality between a pair of ValidationErrorLogs.

        One error log is empty. The other has errors in.
        The empty log is extended with the values in the log that has values.
        """
        assert error_log != error_log_with_error
        assert error_log_with_error != error_log

        error_log.extend(error_log_with_error)

        assert error_log == error_log_with_error
        assert error_log_with_error == error_log

    def test_error_log_extend_from_list(self, error_log, error, warning):
        """Test extending an error log with values from a list.

        The list contains ValidationErrors.
        """
        to_extend = [error, warning]
        error_log.extend(to_extend)

        assert len(error_log) == 2
        assert error in error_log
        assert warning in error_log

    def test_error_log_extend_from_error_log(self, error_log, error_log_mixed_contents):
        """Test extending an error log with values from another error log."""
        error_log.extend(error_log_mixed_contents)

        assert len(error_log) == 2

    @pytest.mark.parametrize("iterable", iati.core.tests.utilities.generate_test_types(['bytearray', 'iter', 'list', 'mapping', 'memory', 'range', 'set', 'str', 'tuple', 'view']))
    def test_error_log_extend_from_iterable(self, error_log, iterable):
        """Test extending an error log with a iterable.

        None of the iterables contain ValidationErrors.
        """
        error_log.extend(iterable)

        assert len(error_log) == 0

    @pytest.mark.parametrize("non_iterable", iati.core.tests.utilities.generate_test_types(['bytearray', 'iter', 'list', 'mapping', 'memory', 'range', 'set', 'str', 'tuple', 'view'], True))
    def test_error_log_extend_from_non_iterable(self, error_log, non_iterable):
        """Test extending an error log with a non-iterable."""
        with pytest.raises(TypeError):
            error_log.extend(non_iterable)

        assert len(error_log) == 0


class TestValidationAuxiliaryData(object):
    """A container for tests relating to auxiliary validation data."""


    def test_error_code_names(self):
        """Check that the names of error codes are all in the correct format."""
        for err_code_name in iati.validator.get_error_codes().keys():
            assert err_code_name.split('-')[0] in ['err', 'warn']

    def test_error_code_attributes(self):
        """Check that error codes have the required attributes."""
        expected_attributes = [
            ('base_exception', type),
            ('category', str),
            ('description', str),
            ('info', str),
            ('help', str)
        ]
        for err_code_name, err_code in iati.validator.get_error_codes().items():
            code_attrs = err_code.keys()
            for (attr_name, attr_type) in expected_attributes:
                assert attr_name in code_attrs
                assert isinstance(err_code[attr_name], attr_type)


class ValidationTestBase(object):
    """A container for fixtures and other functionality useful among multiple groups of Validation Test."""

    @pytest.fixture
    def schema_basic(self):
        """An Activity Schema with no Codelists added."""
        return iati.core.default.activity_schema(None, False)

    @pytest.fixture(params=[
        iati.core.tests.utilities.load_as_string('valid_not_iati'),
        iati.core.tests.utilities.load_as_string('valid_iati'),
        iati.core.tests.utilities.load_as_string('valid_iati_invalid_code'),
        iati.core.tests.utilities.load_as_string('leading_whitespace_xml')
    ])
    def xml_str(self, request):
        """A valid XML string."""
        return request.param

    @pytest.fixture
    def xml_str_no_text_decl(self, xml_str):
        """A valid XML string with the text declaration removed."""
        return '\n'.join(xml_str.strip().split('\n')[1:])

    @pytest.fixture(params=iati.core.tests.utilities.generate_test_types([], True) + [iati.core.tests.utilities.load_as_string('invalid')])
    def not_xml(self, request):
        """A value that is not a valid XML string."""
        return request.param

    @pytest.fixture(params=['This is a string that is not XML.'])
    def str_not_xml(self, request):
        """A string that is not XML.

        Note:
            Does not use the utility function due to problems with Python 2.7.
        """
        return request.param

    @pytest.fixture
    def empty_str(self):
        """An empty string."""
        return ''

    @pytest.fixture(params=[
         iati.core.tests.utilities.load_as_dataset('valid_iati'),
         iati.core.tests.utilities.load_as_dataset('valid_iati_invalid_code')
    ])
    def iati_dataset(self, request):
        """A Dataset that is valid against the IATI Schema."""
        return request.param

    @pytest.fixture(params=[
         iati.core.tests.utilities.load_as_dataset('valid_not_iati')
    ])
    def not_iati_dataset(self, request):
        """A Dataset that is not valid against the IATI Schema."""
        return request.param

    @pytest.fixture(params=[
        iati.core.tests.utilities.load_as_dataset('invalid_iati_missing_required_element'),
        iati.core.tests.utilities.load_as_dataset('invalid_iati_missing_required_element_from_common')
    ])
    def not_iati_dataset_missing_required_el(self, request):
        """A Dataset that is not valid against the IATI Schema because it is missing a required element."""
        return request.param

    @pytest.fixture(params=iati.core.resources.get_test_data_paths_in_folder('ssot-activity-xml-pass'))
    def iati_dataset_valid_from_ssot(self, request):
        """A `should-pass` Dataset from the SSOT."""
        return iati.core.resources.load_as_dataset(request.param)
        return iati.core.Dataset(xml_str)

    @pytest.fixture(params=iati.core.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail'))
    def iati_dataset_invalid_from_ssot(self, request):
        """A `should-fail` Dataset from the SSOT."""
        return iati.core.resources.load_as_dataset(request.param)


class ValidateCodelistsBase(ValidationTestBase):
    """A container for fixtures required for Codelist validation tests."""

    @pytest.fixture
    def schema_version(self):
        """Return an Activity Schema with the Version Codelist added."""
        schema = iati.core.default.activity_schema(None, False)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_org_type(self):
        """Return an Activity Schema with the OrganisationType Codelist added."""
        schema = iati.core.default.activity_schema(None, False)
        codelist = iati.core.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_incomplete_codelist(self):
        """Return an Activity Schema with an incomplete Codelist added."""
        schema = iati.core.default.activity_schema(None, False)
        codelist = iati.core.default.codelists()['Country']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_short_mapping_codelist(self):
        """Return an Activity Schema with a Codelist that has a short `path` in the mapping file."""
        schema = iati.core.default.activity_schema(None, False)
        codelist = iati.core.default.codelists()['Language']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_sectors(self):
        """Return an Activity Schema with the DAC Sector Codelists and appropriate vocabulary added."""
        schema = iati.core.default.activity_schema(None, False)

        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        return schema


class TestValidationTruthyIATI(ValidationTestBase):
    """A container for tests relating to truthy validation of IATI data."""

    def test_basic_validation_valid(self, schema_basic):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_basic)
        assert iati.validator.is_valid(data, schema_basic)

    def test_basic_validation_should_pass_from_ssot(self, iati_dataset_valid_from_ssot, schema_basic):
        """Perform check to see whether a parameter is valid IATI XML.

        The parameter is valid IATI XML. It is sourced from the SSOT.
        """
        assert iati.validator.is_iati_xml(iati_dataset_valid_from_ssot, schema_basic)

    def test_basic_validation_invalid(self, schema_basic):
        """Perform a super simple data validation against an invalid Dataset."""
        data = iati.core.tests.utilities.load_as_dataset('valid_not_iati')

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema_basic)
        assert not iati.validator.is_valid(data, schema_basic)

    def test_basic_validation_should_fail_from_ssot(self, iati_dataset_invalid_from_ssot, schema_basic):
        """Perform check to see whether a parameter is valid IATI XML.

        The parameter is not valid IATI XML. It is sourced from the SSOT.
        """
        assert not iati.validator.is_iati_xml(iati_dataset_invalid_from_ssot, schema_basic)

    def test_basic_validation_invalid_missing_required_element(self, schema_basic):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element."""
        data = iati.core.tests.utilities.load_as_dataset('invalid_iati_missing_required_element')

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema_basic)
        assert not iati.validator.is_valid(data, schema_basic)

    def test_basic_validation_invalid_missing_required_element_from_common(self, schema_basic):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element that is defined in iati-common.xsd."""
        data = iati.core.tests.utilities.load_as_dataset('invalid_iati_missing_required_element_from_common')

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema_basic)
        assert not iati.validator.is_valid(data, schema_basic)


class TestValidateIsXML(ValidationTestBase):
    """A container for tests checking whether a value is valid XML."""


    def test_xml_check_valid_xml(self, xml_str):
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML."""
        assert iati.validator.is_xml(xml_str)

    def test_xml_check_empty_string(self, empty_str):
        """Perform check to ensure an empty string is not valid XML."""
        assert not iati.validator.is_xml(empty_str)

    def test_xml_check_not_xml(self, not_xml):
        """Perform check to see whether a parameter is valid XML. The parameter is not valid XML."""
        assert not iati.validator.is_xml(not_xml)

    def test_xml_check_valid_xml_in_dataset(self, xml_str):
        """Perform check to see whether a Dataset is deemed valid XML."""
        data = iati.core.Dataset(xml_str)

        assert iati.validator.is_xml(data)

    def test_xml_check_valid_xml_detailed_output(self, xml_str):
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML.
        Obtain detailed error output.
        """
        result = iati.validator.validate_is_xml(xml_str)

        assert len(result) == 0

    def test_xml_check_valid_xml_comments_after_detailed_output(self, xml_str, str_not_xml):
        """Perform check to see string a parameter is valid XML.

        The string is valid XML.
        There is a comment added after the XML.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        xml_with_comments = xml_str + comment

        result = iati.validator.validate_is_xml(xml_with_comments)

        assert len(result) == 0

    def test_xml_check_valid_xml_str_comments_before_no_text_decl_detailed_output(self, xml_str_no_text_decl, str_not_xml):
        """Perform check to see whether a string is valid XML.

        The string is valid XML.
        There is a comment added before the XML. There is no XML text declaration.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        xml_prefixed_with_comment = comment + xml_str_no_text_decl

        result = iati.validator.validate_is_xml(xml_prefixed_with_comment)

        assert len(result) == 0

    def test_xml_check_valid_xml_in_dataset_detailed_output(self, xml_str):
        """Perform check to see whether a Dataset is valid XML.

        Obtain detailed error output.
        """
        data = iati.core.Dataset(xml_str)

        result = iati.validator.validate_is_xml(data)

        assert len(result) == 0

    @pytest.mark.parametrize("not_str", iati.core.tests.utilities.generate_test_types(['str'], True))
    def test_xml_check_not_str_detailed_output(self, not_str):
        """Perform check to see whether a parameter is valid XML. The parameter is not valid XML.

        Obtain detailed error output.
        """
        result = iati.validator.validate_is_xml(not_str)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-not-string')

    def test_xml_check_not_xml_str_no_start_tag_detailed_output(self, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string has no XML start tag.
        Obtain detailed error output.
        """
        result = iati.validator.validate_is_xml(str_not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-empty-document')

    def test_xml_check_not_xml_str_text_before_xml_detailed_output(self, str_not_xml, xml_str):
        """Perform check to locate the XML Syntax Errors in a string.

        The string has non-XML text before the XML starts.
        Obtain detailed error output.
        """
        not_xml = str_not_xml + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-empty-document')

    def test_xml_check_not_xml_str_comments_before_detailed_output(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        There is a comment added before the XML. The XML contains a text declaration.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        not_xml = comment + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-xml-text-decl-only-at-doc-start')

    def test_xml_check_not_xml_str_text_after_xml_detailed_output(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string has non-XML text before the XML starts.
        Obtain detailed error output.
        """
        not_xml = xml_str + str_not_xml

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-content-at-end')

    def test_xml_check_not_xml_str_xml_after_xml_detailed_output(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string is two concatenated XML strings. Each contains a text declaration.
        Obtain detailed error output.
        """
        not_xml = xml_str + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert len(result) == 2
        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-content-at-end')
        assert result.contains_error_called('err-not-xml-xml-text-decl-only-at-doc-start')

    def test_xml_check_not_xml_str_xml_after_xml_no_text_decl_detailed_output(self, xml_str_no_text_decl, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string is two concatenated XML strings. Each contains a text declaration.
        Obtain detailed error output.
        """
        not_xml = xml_str_no_text_decl + xml_str_no_text_decl

        result = iati.validator.validate_is_xml(not_xml)

        assert len(result) == 1
        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-content-at-end')


class TestIsValidIATIXML(ValidationTestBase):
    """A container for tests checking whether a value is valid IATI XML."""


    def test_iati_xml_check_valid_xml(self, iati_dataset, schema_basic):
        """Perform check to see whether a parameter is valid IATI XML. The parameter is valid IATI XML."""
        result = iati.validator.validate_is_iati_xml(iati_dataset, schema_basic)

        assert len(result) == 0

    def test_iati_xml_check_not_xml(self, not_iati_dataset, schema_basic):
        """Perform check to see whether a parameter is valid IATI XML.

        The parameter is not valid IATI XML.
        """
        result = iati.validator.validate_is_iati_xml(not_iati_dataset, schema_basic)

        assert result.contains_errors()

    def test_iati_xml_missing_required_element(self, not_iati_dataset_missing_required_el, schema_basic):
        """Perform check to see whether a parameter is valid IATI XML.

        The parameter is not valid IATI XML. It is missing a required element.
        """
        result = iati.validator.validate_is_iati_xml(not_iati_dataset_missing_required_el, schema_basic)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-iati-xml-missing-required-element')

    def test_iati_xml_from_ssot_valid(self, schema_basic):
        """Perform check to see whether valid XML from the SSOT can be loaded and validated."""
        data = iati.core.tests.utilities.load_as_dataset('ssot-activity-xml-pass/location/01-generic-location')

        result = iati.validator.validate_is_iati_xml(data, schema_basic)

        assert len(result) == 0

    def test_iati_xml_from_ssot_invalid(self, schema_basic):
        """Perform check to see whether invalid XML from the SSOT can be loaded and validated."""
        data = iati.core.tests.utilities.load_as_dataset('ssot-activity-xml-fail/other-identifier/01-missing-attribute-type')

        result = iati.validator.validate_is_iati_xml(data, schema_basic)

        assert result.contains_errors()


class TestValidationCodelist(ValidateCodelistsBase):
    """A container for tests relating to validation of Codelists."""


    def test_basic_validation_codelist_valid(self, schema_version):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_version)
        assert iati.validator.is_valid(data, schema_version)

    def test_basic_validation_codelist_invalid(self, schema_version):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_invalid_code')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_version)
        assert not iati.validator.is_valid(data, schema_version)

    def test_basic_validation_codelist_valid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_valid_code_from_common')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codelist_invalid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_invalid_code_from_common')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert not iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codes_valid_multi_use_codelist(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_valid_codes_multiple_xpaths_for_codelist')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert iati.validator.is_valid(data, schema_org_type)

    @pytest.mark.parametrize("data", [iati.core.tests.utilities.load_as_dataset('valid_iati_invalid_codes_multiple_xpaths_for_codelist_first'), iati.core.tests.utilities.load_as_dataset('valid_iati_invalid_codes_multiple_xpaths_for_codelist_second')])
    def test_basic_validation_codes_invalid_multi_use_codelist(self, data, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert not iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codelist_incomplete_present(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is on the list."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_incomplete_codelist_code_present')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_incomplete_codelist)
        assert iati.validator.is_valid(data, schema_incomplete_codelist)

    def test_basic_validation_codelist_incomplete_not_present(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is not on the list."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_incomplete_codelist_code_not_present')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_incomplete_codelist)
        assert iati.validator.is_valid(data, schema_incomplete_codelist)

    def test_basic_validation_short_mapping_xpath(self, schema_short_mapping_codelist):
        """Perform data validation against valid IATI XML. The attribute being tested refers to a Codelist with an abnormally short mapping file path. The data has no attributes mapped to by the Codelist."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_short_mapping_codelist)
        assert iati.validator.is_valid(data, schema_short_mapping_codelist)


class TestValidationVocabularies(ValidateCodelistsBase):
    """A container for tests relating to validation of vocabularies and associated Codelists."""


    def test_validation_codelist_vocab_default_implicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_default_implicit')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_implicit_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set. The code is invalid."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_default_implicit_invalid_code')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_explicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as the default value."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_default_explicit')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_non_default(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as a valid non-default value. The code is valid against this non-default vocabulary."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_non_default')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_multiple_same_valid')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_multiple_different_valid')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_multiple_same_invalid_code')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_multiple_different_invalid_code')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_user_defined(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. No URI is defined, so the code cannot be checked."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_user_defined')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is valid."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_user_defined_with_uri_readable')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable_bad_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is not in the list.

        Todo:
            Check that this is a legitimate check to be performed, given the contents and guidance given in the Standard.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_user_defined_with_uri_readable_bad_code')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_unreadable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a non-machine-readable codelist. As such, the @code cannot be checked. The @code is valid.

        Todo:
            Remove xfail and work on functionality to fully fetch and parse user-defined codelists after higher priority functionality is finished.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_vocab_user_defined_with_uri_unreadable')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)


class TestValidateRulesets(object):
    """A container for tests relating to validation of Rulesets."""

    def test_basic_validation_ruleset_valid(self, schema_ruleset):
        """Perform data validation against valid IATI XML that is valid against the Standard Ruleset."""
        data = iati.core.tests.utilities.load_as_dataset('valid_std_ruleset')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert iati.validator.is_valid(data, schema_ruleset)

    @pytest.mark.parametrize("invalid_xml_file", ['invalid_std_ruleset_bad_date_order', 'invalid_std_ruleset_bad_identifier', 'invalid_std_ruleset_does_not_sum_100', 'invalid_std_ruleset_missing_sector_element'])
    def test_basic_validation_ruleset_invalid(self, schema_ruleset, invalid_xml_file):
        """Perform data validation against valid IATI XML that does not conform to the Standard Ruleset."""
        data = iati.core.tests.utilities.load_as_dataset(invalid_xml_file)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert not iati.validator.is_valid(data, schema_ruleset)

    def test_one_ruleset_error_added_for_multiple_rule_errors(self, schema_ruleset):
        """Check that a Dataset containing multiple Rule errors produces an error log containing only one Ruleset error."""
        data_with_multiple_rule_errors = iati.core.tests.utilities.load_as_dataset('invalid_std_ruleset_multiple_rule_errors')
        result = iati.validator.full_validation(data_with_multiple_rule_errors, schema_ruleset)

        assert len(result.get_errors_or_warnings_by_category('rule')) > 1
        assert len(result.get_errors_or_warnings_by_name('err-ruleset-conformance-fail')) == 1

    def test_multiple_ruleset_error_added_for_multiple_rulesets(self):
        """Check that a Schema containing multiple Rulesets produces an error log containing multiple Ruleset errors when each errors."""
        data_with_multiple_rule_errors = iati.core.tests.utilities.load_as_dataset('invalid_std_ruleset_multiple_rule_errors')
        ruleset_1 = iati.core.default.ruleset()
        ruleset_2 = iati.core.default.ruleset()
        schema = iati.core.default.activity_schema(None, False)
        schema.rulesets.add(ruleset_1)
        schema.rulesets.add(ruleset_2)
        result = iati.validator.full_validation(data_with_multiple_rule_errors, schema)

        assert len(result.get_errors_or_warnings_by_category('rule')) > 1
        assert len(result.get_errors_or_warnings_by_name('err-ruleset-conformance-fail')) == 2

    def test_no_ruleset_errors_added_for_rule_warnings(self, schema_ruleset):
        """Check that a Dataset containing only Rule warnings does not result in a Ruleset error being added."""
        data_with_rule_warnings_only = iati.core.tests.utilities.load_as_dataset('valid_std_ruleset')
        result = iati.validator.full_validation(data_with_rule_warnings_only, schema_ruleset)

        assert len(result.get_warnings()) > 0
        assert len(result.get_errors_or_warnings_by_category('rule')) > 0
        assert len(result.get_errors_or_warnings_by_name('err-ruleset-conformance-fail')) == 0


class TestValidatorFullValidation(ValidateCodelistsBase):
    """A container for tests relating to detailed error output from validation."""

    def test_full_validation_codelist_valid_detailed_output(self, schema_version):
        """Perform data validation against valid IATI XML that has valid Codelist values.  Obtain detailed error output."""
        data = iati.core.tests.utilities.load_as_dataset('valid_iati')

        assert iati.validator.full_validation(data, schema_version) == iati.validator.ValidationErrorLog()

    def test_full_validation_codelist_invalid_detailed_output(self, schema_version):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        xml_str = iati.core.tests.utilities.load_as_string('valid_iati_invalid_code')
        data = iati.core.Dataset(xml_str)

        result = iati.validator.full_validation(data, schema_version)[0]

        assert isinstance(result, iati.validator.ValidationError)
        assert result.name == 'err-code-not-on-codelist'
        assert result.status == 'error'
        assert result.line_number == 3
        assert result.context == '\n'.join(xml_str.split('\n')[1:4])
        assert 'Version' in result.info
        assert 'Version' in result.help

    def test_full_validation_codelist_incomplete_present_detailed_output(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is on the list.
        Obtain detailed error output.
        """
        data = iati.core.tests.utilities.load_as_dataset('valid_iati_incomplete_codelist_code_present')

        result = iati.validator.full_validation(data, schema_incomplete_codelist)

        assert len(result) == 0

    def test_full_validation_codelist_incomplete_not_present_detailed_output(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is not on the list.
        Obtain detailed error output.
        """
        xml_str = iati.core.tests.utilities.load_as_string('valid_iati_incomplete_codelist_code_not_present')
        data = iati.core.Dataset(xml_str)

        result = iati.validator.full_validation(data, schema_incomplete_codelist)[0]

        assert result.name == 'warn-code-not-on-codelist'
        assert result.line_number == 18
        assert result.context == '\n'.join(xml_str.split('\n')[16:19])
        assert result.status == 'warning'
        assert 'Country' in result.info
        assert 'Country' in result.help

    def test_full_validation_not_xml_detailed_output(self, schema_basic):
        """Perform full validation against a string that is not XML."""
        not_xml = 'This is not XML.'

        result = iati.validator.full_validation(not_xml, schema_basic)

        assert len(result) == 1
        assert result.contains_error_called('err-not-xml-empty-document')
