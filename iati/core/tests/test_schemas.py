import pytest

import iati.core.schemas

class TestSchemas(object):
    """A container for tests relating to Schemas"""

    def test_schema_default_attributes(self):
        """Check a Schema's default attributes are correct"""
        schema = iati.core.schemas.Schema()

        assert None == schema.name

    def test_schema_name_instance(self):
        """Check a Schema's attributes are correct when defined with only a name"""
        name_to_set = "test Codelist name"
        schema = iati.core.schemas.Schema(name_to_set)

        assert name_to_set == schema.name
