"""A module containing tests for the library representation of default values."""
import pytest
import iati.core.codelists
import iati.core.default
import iati.core.schemas


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelist_valid(self):
        """Check that a named default Codelist may be located.

        Todo:
            Handle multiple versions.

            Check internal values beyond the codelists being the correct type.
        """
        name = 'Country'
        codelist = iati.core.default.codelist(name)

        assert isinstance(codelist, iati.core.Codelist)
        assert codelist.name == name
        for code in codelist.codes:
            assert isinstance(code, iati.core.Code)

    @pytest.mark.parametrize("name", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_default_codelist_invalid(self, name):
        """Check that trying to find a default Codelist with an invalid name raises an error."""
        with pytest.raises(ValueError) as excinfo:
            iati.core.default.codelist(name)

        assert 'There is no default Codelist in version' in str(excinfo.value)

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
            assert isinstance(codelist, iati.core.Codelist)

    def test_default_ruleset(self):
        """Check that the default Ruleset is correct.

        Todo:
            Handle multiple versions.

            Check internal values beyond the Ruleset being the correct type.
        """
        ruleset = iati.core.default.ruleset()

        assert isinstance(ruleset, iati.core.rulesets.Ruleset)

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
            assert isinstance(schema, iati.core.Schema)
