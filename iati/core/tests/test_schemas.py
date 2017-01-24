import pytest

import iati.core.schemas

class TestSchemas(object):
    """A container for tests relating to Schemas"""

    def test_schema_default_attributes(self):
        """Check a Schema's default attributes are correct"""
        schema = iati.core.schemas.Schema()

        assert None == schema.name
