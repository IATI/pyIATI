"""A module containing tests for the library representation of default values."""
import iati.core.codelists
import iati.core.default
import iati.core.schemas


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelists(self):
        """Check that the default Codelists are correct.

        Todo:
            Handle multiple versions.

            Check internal values beyond the codelists being the correct type.
        """
        codelists = iati.core.default.codelists()

        assert isinstance(codelists, dict)
        assert len(codelists) == 62
        for _, codelist in codelists.items():
            assert isinstance(codelist, iati.core.codelists.Codelist)

    def test_default_schemas(self):
        """Check that the default Schemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.

            Check for the correct number of Schemas.
        """
        schemas = iati.core.default.schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == 1
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.schemas.Schema)
