"""A module containing tests for data validation."""
from lxml import etree
import pytest
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.test.utilities
import iati.validate


class TestValidate(object):
    """A container for tests relating to validation."""

    def test_basic_validation_valid(self):
        """Perform super simple data validation against a valid dataset"""
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.test.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_invalid(self):
        """Perform super simple data validation against a valid dataset"""
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID)
        schema = iati.core.schemas.Schema(name=iati.core.test.utilities.SCHEMA_NAME_VALID)

        assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_valid(self):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID_IATI)
        schema = iati.core.schemas.Schema(name=iati.core.test.utilities.SCHEMA_NAME_VALID)
        schema.codelists.add(iati.core.default.codelists()['Country'])

        assert len(schema.codelists) == 1
        assert iati.validate.is_valid(data, schema)

    @pytest.mark.xfail
    def test_basic_validation_codelist_invalid(self):
        """Perform data validation against valid IATI XML that has an invalid Codelist value.

        Todo:
            Determine why this test is flaky.
        """
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID_IATI_INVALID_CODE)
        schema = iati.core.schemas.Schema(name=iati.core.test.utilities.SCHEMA_NAME_VALID)
        schema.codelists.add(iati.core.default.codelist('Country'))

        assert len(schema.codelists) == 1
        assert not iati.validate.is_valid(data, schema)
