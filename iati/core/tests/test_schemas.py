"""A module containing tests for the library representation of Schemas."""
from lxml.etree import XMLSchema
import iati.core.exceptions
import iati.core.schemas


class TestSchemas(object):
    """A container for tests relating to Schemas"""

    def test_schema_default_attributes(self):
        """Check a Schema's default attributes are correct"""
        schema = iati.core.schemas.Schema()

        assert schema.name is None

    def test_schema_name_instance(self):
        """Check a Schema's attributes are correct when defined with only a name"""
        name_to_set = "test Schema name"
        try:
            schema = iati.core.schemas.Schema(name_to_set)
        except iati.core.exceptions.SchemaError:
            assert True
        else:
            # an exception should be raised
            assert False

    def test_schema_define_from_xsd(self):
        """Check that a Schema can be generated from an XSD definition"""
        schema_name = 'iati-activities-schema'

        schema = iati.core.schemas.Schema(name=schema_name)

        assert schema.name == schema_name
        assert isinstance(schema.schema, XMLSchema)
