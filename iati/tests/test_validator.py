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

    @pytest.mark.parametrize("invalid_err_name", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_validation_error_init_bad_name_type(self, invalid_err_name):
        """Test that a ValidationError cannot be created with a name that does not exist."""
        with pytest.raises(ValueError):
            iati.validator.ValidationError(invalid_err_name)

    def test_error_log_init_valid_name(self):
        """Test that a ValidationError can be created when provided a valid name."""
        err_name = 'err-code-not-on-codelist'
        err = iati.validator.ValidationError(err_name)
        err_detail = iati.validator._ERROR_CODES[err_name]

        assert isinstance(err, iati.validator.ValidationError)
        assert err.name == err_name
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
    def error(self, err_name):
        """An error."""
        return iati.validator.ValidationError(err_name)

    @pytest.fixture
    def warning_name(self):
        """The name of a warning."""
        return 'warn-code-not-on-codelist'

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

    def test_error_log_add_errors(self, error_log_with_error, err_name, warning_name):
        """Test that errors are identified as errors when added to the error log."""
        assert len(error_log_with_error) == 1
        assert error_log_with_error.contains_errors()
        assert not error_log_with_error.contains_warnings()
        assert error_log_with_error.contains_error_called(err_name)
        assert not error_log_with_error.contains_error_called(warning_name)

    def test_error_log_add_warnings(self, error_log_with_warning, err_name, warning_name):
        """Test that warnings are not identified as errors when added to the error log."""
        assert len(error_log_with_warning) == 1
        assert not error_log_with_warning.contains_errors()
        assert error_log_with_warning.contains_warnings()
        assert not error_log_with_warning.contains_error_called(err_name)
        assert error_log_with_warning.contains_error_called(warning_name)

    def test_error_log_add_mixed(self, error_log_mixed_contents, err_name, warning_name):
        """Test that a mix of errors and warnings are identified as such when added to the error log."""
        assert len(error_log_mixed_contents) == 2
        assert error_log_mixed_contents.contains_errors()
        assert error_log_mixed_contents.contains_warnings()
        assert error_log_mixed_contents.contains_error_called(err_name)
        assert error_log_mixed_contents.contains_error_called(warning_name)

    @pytest.mark.parametrize("not_ValidationError", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_error_log_add_incorrect_type(self, error_log, not_ValidationError):
        """Test that you may only add ValidationErrors to a ValidationErrorLog."""
        with pytest.raises(TypeError):
            error_log.add(not_ValidationError)

    @pytest.mark.parametrize("potential_ValidationError", iati.core.tests.utilities.find_parameter_by_type([], False) + [iati.validator.ValidationError('err-code-not-on-codelist')])
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
        """Test extending an error log with values from a list."""
        to_extend = [error, warning]
        error_log.extend(to_extend)

        assert len(error_log) == 2
        assert error in error_log
        assert warning in error_log

    def test_error_log_extend_from_error_log(self, error_log, error_log_mixed_contents):
        """Test extending an error log with values from another error log."""
        error_log.extend(error_log_mixed_contents)

        assert len(error_log) == 2


class TestValidation(object):
    """A container for tests relating to validation."""

    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema)
        assert iati.validator.is_valid(data, schema)

    def test_basic_validation_invalid(self):
        """Perform a super simple data validation against an invalid Dataset."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema)
        assert not iati.validator.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema)
        assert not iati.validator.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element_from_common(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element that is defined in iati-common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT_COMMON)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert not iati.validator.is_iati_xml(data, schema)
        assert not iati.validator.is_valid(data, schema)

    def test_error_code_names(self):
        """Check that the names of error codes are all in the correct format."""
        for err_code_name in iati.validator._ERROR_CODES.keys():
            assert err_code_name.split('-')[0] in ['err', 'warn']

    def test_error_code_attributes(self):
        """Check that error codes have the required attributes."""
        expected_attributes = ['category', 'description', 'info', 'help']
        for err_code_name, err_code in iati.validator._ERROR_CODES.items():
            code_attrs = err_code.keys()
            for attr in expected_attributes:
                assert attr in code_attrs
                assert isinstance(err_code[attr], str)


class TestValidateIsXML(object):
    """A container for tests checking whether a value is valid XML."""


    @pytest.fixture(params=[
        iati.core.tests.utilities.XML_STR_VALID_NOT_IATI,
        iati.core.tests.utilities.XML_STR_VALID_IATI,
        iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE,
        iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE
    ])
    def xml_str(self, request):
        """A valid XML string."""
        return request.param

    @pytest.fixture(params=iati.core.tests.utilities.find_parameter_by_type(['str'], False) + [iati.core.tests.utilities.XML_STR_INVALID])
    def not_xml(self, request):
        """A value that is not a valid XML string."""
        return request.param

    @pytest.fixture
    def str_not_xml(self):
        """A string that is not XML."""
        return 'This is not XML.'

    def test_xml_check_valid_xml(self, xml_str):
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML."""
        assert iati.validator.is_xml(xml_str)

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
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML.

        There is a comment added after the XML.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        xml_with_comments = xml_str + comment

        result = iati.validator.validate_is_xml(xml_with_comments)

        assert len(result) == 0

    def test_xml_check_valid_xml_str_comments_before_no_prolog(self, xml_str, str_not_xml):
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML.

        There is a comment added before the XML. There is no XMl prolog.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        xml_prefixed_with_comment = comment + '\n'.join(xml_str.strip().split('\n')[1:])

        result = iati.validator.validate_is_xml(xml_prefixed_with_comment)

        assert len(result) == 0

    def test_xml_check_valid_xml_in_dataset_detailed_output(self, xml_str):
        """Perform check to see whether a Dataset is valid XML.
        Obtain detailed error output.
        """
        data = iati.core.Dataset(xml_str)

        result = iati.validator.validate_is_xml(data)

        assert len(result) == 0

    @pytest.mark.parametrize("not_str", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_xml_check_not_str_detailed_output(self, not_str):
        """Perform check to see whether a parameter is valid XML. The parameter is not valid XML.
        Obtain detailed error output.
        """
        result = iati.validator.validate_is_xml(not_str)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-not-string')

    def test_xml_check_not_xml_str_no_start_tag(self, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.
        The string has no XML start tag.
        """
        result = iati.validator.validate_is_xml(str_not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-empty-document')

    def test_xml_check_not_xml_str_text_before_xml(self, str_not_xml, xml_str):
        """Perform check to locate the XML Syntax Errors in a string.

        The string has non-XML text before the XML starts.
        """
        not_xml = str_not_xml + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-empty-document')

    def test_xml_check_not_xml_str_comments_before(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        There is a comment added before the XML. The XML contains a prolog.
        Obtain detailed error output.
        """
        comment = '<!-- ' + str_not_xml + ' -->'
        not_xml = comment + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-xml-prolog-only-at-doc-start')

    def test_xml_check_not_xml_str_text_after_xml(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string has non-XML text before the XML starts.
        """
        not_xml = xml_str + str_not_xml

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-content-at-end')

    def test_xml_check_not_xml_str_xml_after_xml(self, xml_str, str_not_xml):
        """Perform check to locate the XML Syntax Errors in a string.

        The string is two concatenated XML filed.
        """
        not_xml = xml_str + xml_str

        result = iati.validator.validate_is_xml(not_xml)

        assert result.contains_errors()
        assert result.contains_error_called('err-not-xml-content-at-end')
        assert result.contains_error_called('err-not-xml-xml-prolog-only-at-doc-start')


class ValidateCodelistsBase(object):
    """A container for fixtures required for Codelist validation tests."""


    @pytest.fixture
    def schema_version(self):
        """A schema with the Version Codelist added.

        Returns:
            A valid activity schema with the Version Codelist added.

        """
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_org_type(self):
        """A schema with the OrganisationType Codelist added.

        Returns:
            A valid activity schema with the OrganisationType Codelist added.

        """
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_incomplete_codelist(self):
        """A schema with an incomplete Codelist added.

        Returns:
            A valid activity schema with the OrganisationType Codelist added.

        """
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Country']

        schema.codelists.add(codelist)

        return schema

    @pytest.fixture
    def schema_sectors(self):
        """A schema with the DAC Sector Codelists and appropriate vocabulary added.

        Returns:
            A valid activity schema with the DAC Sector Codelists and appropriate vocabulary added.

        """
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        return schema


class TestValidationCodelist(ValidateCodelistsBase):
    """A container for tests relating to validation of Codelists."""


    def test_basic_validation_codelist_valid(self, schema_version):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_version)
        assert iati.validator.is_valid(data, schema_version)

    def test_basic_validation_codelist_invalid(self, schema_version):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_version)
        assert not iati.validator.is_valid(data, schema_version)

    def test_basic_validation_codelist_valid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VALID_CODE_FROM_COMMON)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codelist_invalid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE_FROM_COMMON)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert not iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codes_valid_multi_use_codelist(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert iati.validator.is_valid(data, schema_org_type)

    @pytest.mark.parametrize("xml_str", [iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST_FIRST, iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST_SECOND])
    def test_basic_validation_codes_invalid_multi_use_codelist(self, xml_str, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        data = iati.core.Dataset(xml_str)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_org_type)
        assert not iati.validator.is_valid(data, schema_org_type)

    def test_basic_validation_codelist_incomplete_present(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is on the list."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INCOMPLETE_CODELIST_CODE_PRESENT)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_incomplete_codelist)
        assert iati.validator.is_valid(data, schema_incomplete_codelist)

    def test_basic_validation_codelist_incomplete_not_present(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is not on the list."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INCOMPLETE_CODELIST_CODE_NOT_PRESENT)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_incomplete_codelist)
        assert iati.validator.is_valid(data, schema_incomplete_codelist)


class TestValidationVocabularies(ValidateCodelistsBase):
    """A container for tests relating to validation of vocabularies and associated Codelists."""


    def test_validation_codelist_vocab_default_implicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_implicit_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set. The code is invalid."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT_INVALID_CODE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_explicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as the default value."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_EXPLICIT)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_non_default(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as a valid non-default value. The code is valid against this non-default vocabulary."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_NON_DEFAULT)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_SAME_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_DIFFERENT_VALID)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_SAME_INVALID_CODE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_DIFFERENT_INVALID_CODE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_user_defined(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. No URI is defined, so the code cannot be checked."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is valid."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable_bad_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is not in the list.

        Todo:
            Check that this is a legitimate check to be performed, given the contents and guidance given in the Standard.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE_BAD_CODE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert not iati.validator.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_unreadable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a non-machine-readable codelist. As such, the @code cannot be checked. The @code is valid.

        Todo:
            Remove xfail and work on functionality to fully fetch and parse user-defined codelists after higher priority functionality is finished.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_UNREADABLE)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_sectors)
        assert iati.validator.is_valid(data, schema_sectors)


class TestValidatorDetailedOutput(ValidateCodelistsBase):
    """A container for tests relating to detailed error output from validation."""

    def test_basic_validation_codelist_valid_detailed_output(self, schema_version):
        """Perform data validation against valid IATI XML that has valid Codelist values.  Obtain detailed error output."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)

        assert iati.validator.full_validation(data, schema_version) == iati.validator.ValidationErrorLog()

    def test_basic_validation_codelist_invalid_detailed_output(self, schema_version):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        xml_str = iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE
        data = iati.core.Dataset(xml_str)

        result = iati.validator.full_validation(data, schema_version)[0]

        assert isinstance(result, iati.validator.ValidationError)
        assert result.status == 'error'
        assert result.line_number == 3
        assert result.context == '\n'.join(xml_str.split('\n')[1:4])
        assert 'Version' in result.info
        assert 'Version' in result.help

    def test_basic_validation_codelist_incomplete_present_detailed_output(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is on the list.
        Obtain detailed error output.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INCOMPLETE_CODELIST_CODE_PRESENT)

        result = iati.validator.full_validation(data, schema_incomplete_codelist)

        assert len(result) == 0

    def test_basic_validation_codelist_incomplete_not_present_detailed_output(self, schema_incomplete_codelist):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested refers to an incomplete Codelist. The value is not on the list.
        Obtain detailed error output.
        """
        xml_str = iati.core.tests.utilities.XML_STR_VALID_IATI_INCOMPLETE_CODELIST_CODE_NOT_PRESENT
        data = iati.core.Dataset(xml_str)

        result = iati.validator.full_validation(data, schema_incomplete_codelist)[0]

        assert result.line_number == 18
        assert result.context == '\n'.join(xml_str.split('\n')[16:19])
        assert result.status == 'warning'
        assert 'Country' in result.info
        assert 'Country' in result.help
