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

        assert isinstance(codelist, iati.core.codelists.Codelist)
        assert codelist.name == name
        for code in codelist.codes:
            assert isinstance(code, iati.core.codelists.Code)

    @pytest.mark.parametrize("name", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_default_codelist_invalid(self, name):
        """Check that trying to find a default Codelist with an invalid name raises an error."""
        try:
            _ = iati.core.default.codelist(name)
        except ValueError:
            assert True
        else:  # pragma: no cover
            assert False

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

    def test_codelist_mapping_condition(self):
        """Check that the Codelist mapping file is being read correctly.

        Todo:
            Split into multiple tests.
        """
        mapping = iati.core.default.codelist_mapping()

        assert mapping['Sector']['condition'] == "@vocabulary = '1' or not(@vocabulary)"
        assert mapping['Version']['condition'] is None

    def test_codelist_mapping_xpath(self):
        """Check that the Codelist mapping file is being read correctly.

        Todo:
            Split into multiple tests.
        """
        mapping = iati.core.default.codelist_mapping()

        assert mapping['Version']['xpath'] == '//iati-activities/@version'
        try:
            _ = mapping['InvalidCodelistName']['xpath']
        except KeyError:
            assert True
        else:  # pragma: no cover
            assert False

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
