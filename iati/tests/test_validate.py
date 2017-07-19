"""A module containing tests for data validation."""
import pytest
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
import iati.validate


class TestValidate(object):
    """A container for tests relating to validation."""

    @pytest.mark.parametrize("xml", [iati.core.tests.utilities.XML_STR_VALID_NOT_IATI, iati.core.tests.utilities.XML_STR_VALID_IATI, iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE, iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE])
    def test_xml_check_valid_xml(self, xml):
        """Perform check to see whether a parameter is valid XML. The parameter is valid XML."""
        assert iati.validate.is_xml(xml)

    @pytest.mark.parametrize("not_xml", iati.core.tests.utilities.find_parameter_by_type(['str'], False) + [iati.core.tests.utilities.XML_STR_INVALID])
    def test_xml_check_not_xml(self, not_xml):
        """Perform check to see whether a parameter is valid XML. The parameter is not valid XML."""
        assert not iati.validate.is_xml(not_xml)

    @pytest.mark.parametrize("xml", [iati.core.tests.utilities.XML_STR_VALID_NOT_IATI, iati.core.tests.utilities.XML_STR_VALID_IATI, iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE, iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE])
    def test_xml_check_valid_xml(self, xml):
        """Perform check to see whether a Dataset is deemed valid XML."""
        data = iati.core.Dataset(xml)

        assert iati.validate.is_xml(data)

    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema)
        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid(self):
        """Perform a super simple data validation against an invalid Dataset."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert not iati.validate.is_iati_xml(data, schema)
        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert not iati.validate.is_iati_xml(data, schema)
        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element_from_common(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element that is defined in iati-common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT_COMMON)
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert not iati.validate.is_iati_xml(data, schema)
        assert not iati.validate.is_valid(data, schema)


class TestValidateCodelist(object):
    """A container for tests relating to validation of Codelists."""

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

    def test_basic_validation_codelist_valid(self, schema_version):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_version)
        assert iati.validate.is_valid(data, schema_version)

    def test_basic_validation_codelist_invalid(self, schema_version):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_version)
        assert not iati.validate.is_valid(data, schema_version)

    def test_basic_validation_codelist_valid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VALID_CODE_FROM_COMMON)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_org_type)
        assert iati.validate.is_valid(data, schema_org_type)

    def test_basic_validation_codelist_invalid_from_common(self, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE_FROM_COMMON)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_org_type)
        assert not iati.validate.is_valid(data, schema_org_type)

    def test_basic_validation_codes_valid_multi_use_codelist(self, schema_org_type):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_org_type)
        assert iati.validate.is_valid(data, schema_org_type)

    @pytest.mark.parametrize("xml_str", [iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST_FIRST, iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODES_MULTIPLE_XPATHS_FOR_CODELIST_SECOND])
    def test_basic_validation_codes_invalid_multi_use_codelist(self, xml_str, schema_org_type):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attributes being tested are under different elements, but require the same Codelist."""
        data = iati.core.Dataset(xml_str)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_org_type)
        assert not iati.validate.is_valid(data, schema_org_type)


class TestValidateVocabularies(object):
    """A container for tests relating to validation of vocabularies and associated Codelists."""

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

    def test_validation_codelist_vocab_default_implicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_implicit_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set. The code is invalid."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT_INVALID_CODE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert not iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_default_explicit(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as the default value."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_EXPLICIT)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_non_default(self, schema_sectors):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as a valid non-default value. The code is valid against this non-default vocabulary."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_NON_DEFAULT)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_SAME_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_valid(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_DIFFERENT_VALID)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_same_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is the same.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_SAME_INVALID_CODE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert not iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_multiple_different_invalid_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with an activity that uses multiple instances of the same element that uses vocabularies.

        The vocabulary used by each of these elements is different.
        The codes are valid against the vocabularies.
        Percentages add up to 100.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_MULTIPLE_DIFFERENT_INVALID_CODE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert not iati.validate.is_valid(data, schema_sectors)

    def test_validation_codelist_vocab_user_defined(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. No URI is defined, so the code cannot be checked."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is valid."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_readable_bad_code(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is not in the list.

        Todo:
            Check that this is a legitimate check to be performed, given the contents and guidance given in the Standard.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE_BAD_CODE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert not iati.validate.is_valid(data, schema_sectors)

    @pytest.mark.skip(reason="Not yet implemented - need to be able to load Codelists from URLs")
    def test_validation_codelist_vocab_user_defined_with_uri_unreadable(self, schema_sectors):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a non-machine-readable codelist. As such, the @code cannot be checked. The @code is valid.

        Todo:
            Remove xfail and work on functionality to fully fetch and parse user-defined codelists after higher priority functionality is finished.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_UNREADABLE)

        assert iati.validate.is_xml(data.xml_str)
        assert iati.validate.is_iati_xml(data, schema_sectors)
        assert iati.validate.is_valid(data, schema_sectors)


class TestValidateRulesets(object):
    """A container for tests relating to validation of Rulesets."""

    @pytest.fixture
    def schema_ruleset(self):
        """A schema with the default Ruleset added.

        Returns:
            A valid activity schema with the Version Codelist added.

        """
        schema = iati.core.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        ruleset = iati.core.default.ruleset()

        schema.rulesets.add(ruleset)

        return schema
