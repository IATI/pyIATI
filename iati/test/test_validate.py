"""A module containing tests for data validation."""
from lxml import etree
import pytest
import iati.core.data
import iati.core.schemas
import iati.core.test.utilities
import iati.validate


class TestValidate(object):
    """A container for tests relating to validation."""

    def test_basic_validation(self):
        """Perform super simple data validation."""
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID)
        schema = iati.core.schemas.Schema(name=iati.core.test.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_valid(data, schema)
