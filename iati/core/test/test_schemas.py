"""A module containing tests for the library representation of Schemas."""
import pytest
from lxml.etree import XMLSchema
import iati.core.codelists
import iati.core.exceptions
import iati.core.schemas
import iati.core.test.utilities


class TestSchemas(object):
    """A container for tests relating to Schemas"""

    @pytest.fixture
    def schema_initialised(self):
        """Create a very basic Schema.

        Returns:
            iati.core.schemas.Schema: A Schema that has been initialised with basic values.
        """
        schema_name = iati.core.test.utilities.SCHEMA_NAME_VALID

        return iati.core.schemas.Schema(name=schema_name)

    def test_schema_default_attributes(self):
        """Check a Schema's default attributes are correct"""
        schema = iati.core.schemas.Schema()

        assert schema.name is None

    @pytest.mark.parametrize("invalid_name", iati.core.test.utilities.find_parameter_by_type(['str', 'none'], False))
    def test_schema_name_instance(self, invalid_name):
        """Check that an Error is raised when attempting to load a Schema that does not exist.

        Todo:
            Check for type errors when the type is incorrect.
        """
        try:
            _ = iati.core.schemas.Schema(invalid_name)
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised, so this point should not be reached
            assert False

    def test_schema_define_from_xsd(self, schema_initialised):
        """Check that a Schema can be generated from an XSD definition"""
        schema = schema_initialised

        assert schema.name == iati.core.test.utilities.SCHEMA_NAME_VALID
        assert isinstance(schema.validator(), XMLSchema)
        assert isinstance(schema.codelists, set)
        assert len(schema.codelists) == 0

    def test_schema_codelists_add(self, schema_initialised):
        """Check that it is possible to add Codelists to the Schema."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_twice(self, schema_initialised):
        """Check that it is not possible to add the same Codelist to a Schema multiple times."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist)

        assert len(schema.codelists) == 1

    def test_schema_codelists_add_duplicate(self, schema_initialised):
        """Check that it is not possible to add multiple functionally identical Codelists to a Schema."""
        codelist_name = "a test Codelist name"
        schema = schema_initialised
        codelist = iati.core.codelists.Codelist(codelist_name)
        codelist2 = iati.core.codelists.Codelist(codelist_name)

        schema.codelists.add(codelist)
        schema.codelists.add(codelist2)

        assert len(schema.codelists) == 1
