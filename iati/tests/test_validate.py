"""A module containing tests for data validation."""
# pylint: disable=no-value-for-parameter,unexpected-keyword-arg
import pytest
import iati.data
import iati.default
import iati.schemas
import iati.tests.utilities
import iati.validate


@pytest.mark.xfail(strict=True)
class TestValidate(object):
    """A container for tests relating to validation."""

    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid activity Dataset."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid(self):
        """Perform a super simple data validation against an invalid activity Dataset."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_not_iati'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element(self):
        """Perform a super simple data validation against an activity Dataset that is invalid due to a missing required element."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('invalid_iati_missing_required_element'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid_missing_required_element_from_common(self):
        """Perform a super simple data validation against an activity Dataset that is invalid due to a missing required element that is defined in iati-common.xsd."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('invalid_iati_missing_required_element_from_common'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_valid(self):
        """Perform data validation against valid IATI activity XML that has valid Codelist values."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist = iati.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_invalid(self):
        """Perform data validation against valid IATI activity XML that has invalid Codelist values."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_invalid_code'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist = iati.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_valid_from_common(self):
        """Perform data validation against valid IATI activity XML that has valid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_valid_code_from_common'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist = iati.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_invalid_from_common(self):
        """Perform data validation against valid IATI activity XML that has invalid Codelist values. The attribute being tested is on an element defined in common.xsd."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_invalid_code_from_common'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist = iati.default.codelists()['OrganisationType']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_default_implicit(self):
        """Perform data validation against valid IATI activity XML with a vocabulary that has been implicitly set."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_default_explicit'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_default_implicit_invalid_code(self):
        """Perform data validation against valid IATI activity XML with a vocabulary that has been implicitly set. The code is invalid."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_default_implicit'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert not iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_default_explicit(self):
        """Perform data validation against valid IATI activity XML with a vocabulary that has been explicitly set as the default value."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_default_explicit'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_non_default(self):
        """Perform data validation against valid IATI activity XML with a vocabulary that has been explicitly set as a valid non-default value. The code is valid against this non-default vocabulary."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_non_default'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_user_defined(self):
        """Perform data validation against valid IATI activity XML with a user-defined vocabulary. No URI is defined, so the code cannot be checked."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_user_defined'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_user_defined_with_uri_readable(self):
        """Perform data validation against valid IATI activity XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is valid."""
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_user_defined_with_uri_readable'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_user_defined_with_uri_readable_bad_code(self):
        """Perform data validation against valid IATI activity XML with a user-defined vocabulary. A URI is defined, and points to a machine-readable codelist. As such, the code can be checked. The @code is not in the list.

        Todo:
            Check that this is a legitimate check to be performed, given the contents and guidance given in the Standard.
        """
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_user_defined_with_uri_readable_bad_code'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert not iati.validate.is_valid(data, schema)

    def test_validation_codelist_vocab_user_defined_with_uri_unreadable(self):
        """Perform data validation against valid IATI activity XML with a user-defined vocabulary. A URI is defined, and points to a non-machine-readable codelist. As such, the @code cannot be checked. The @code is valid.

        Todo:
            Remove xfail and work on functionality to fully fetch and parse user-defined codelists after higher priority functionality is finished.
        """
        data = iati.Dataset(iati.tests.utilities.load_as_string('valid_iati_vocab_user_defined_with_uri_unreadable'))
        schema = iati.ActivitySchema(name=iati.tests.utilities.SCHEMA_ACTIVITY_NAME_VALID)
        codelist_1 = iati.default.codelists()['SectorVocabulary']
        codelist_2 = iati.default.codelists()['Sector']
        codelist_3 = iati.default.codelists()['SectorCategory']

        schema.codelists.add(codelist_1)
        schema.codelists.add(codelist_2)
        schema.codelists.add(codelist_3)

        assert iati.validate.is_valid(data, schema)
