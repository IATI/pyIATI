"""A module containing tests for data validation."""
import pytest
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
import iati.validate


class TestValidate(object):
    """A container for tests relating to validation."""

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_invalid(self):
        """Perform a super simple data validation against an invalid Dataset."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_invalid_missing_required_element(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_invalid_missing_required_element_from_common(self):
        """Perform a super simple data validation against a Dataset that is invalid due to a missing required element that is defined in iati-common.xsd."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_INVALID_IATI_MISSING_REQUIRED_ELEMENT_COMMON)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_codelist_valid(self):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_codelist_invalid(self):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_codelist_valid_from_common(self):
        """Perform data validation against valid IATI XML that has valid Codelist values. The attribute being tested is on an element defined in common.xsd"""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VALID_CODE_FROM_COMMON)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_basic_validation_codelist_invalid_from_common(self):
        """Perform data validation against valid IATI XML that has invalid Codelist values. The attribute being tested is on an element defined in common.xsd"""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE_FROM_COMMON)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_default_implicit(self):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_default_implicit_invalid_code(self):
        """Perform data validation against valid IATI XML with a vocabulary that has been implicitly set. The code is invalid."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_IMPLICIT_INVALID_CODE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_default_explicit(self):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as the default value."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_DEFAULT_EXPLICIT)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_non_default(self):
        """Perform data validation against valid IATI XML with a vocabulary that has been explicitly set as a valid non-default value. The code is valid against this non-default vocabulary."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_NON_DEFAULT)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_user_defined(self):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. No URI is defined, so the code cannot be checked."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_user_defined_with_uri_readable(self):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is valid."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_user_defined_with_uri_readable_bad_code(self):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is not in the list.

        Todo:
            Check that this is a legitimate check to be performed, given the contents and guidance given in the Standard.
        """
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_READABLE_BAD_CODE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert not iati.validate.is_valid(data, schema)

    @pytest.mark.xfail(strict=True)
    def test_validation_codelist_vocab_user_defined_with_uri_unreadable(self):
        """Perform data validation against valid IATI XML with a user-defined vocabulary. A URI is defined, and points to a non-machine-readable codelist. As such, the @code cannot be checked. The @code is valid.

        Todo:
            Remove xfail and work on functionality to fully fetch and parse user-defined codelists after higher priority functionality is finished.
        """
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_VOCAB_USER_DEFINED_WITH_URI_UNREADABLE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist_1 = iati.core.default.codelists()['SectorVocabulary']
        codelist_2 = iati.core.default.codelists()['Sector']
        codelist_3 = iati.core.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)
