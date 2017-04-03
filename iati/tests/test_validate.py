"""A module containing tests for data validation."""
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
import iati.validate


class TestValidate(object):
    """A container for tests relating to validation."""

    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid(self):
        """Perform a super simple data validation against an invalid Dataset."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_valid(self):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_invalid(self):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID_IATI_INVALID_CODE)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)
