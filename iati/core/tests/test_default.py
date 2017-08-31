"""A module containing tests for the library representation of default values."""
import pytest
import iati.core.codelists
import iati.core.constants
import iati.core.default
import iati.core.schemas


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelist_valid(self, standard_version_optional):
        """Check that a named default Codelist may be located.

        Todo:
            Check internal values beyond the codelists being the correct type.
        """
        name = 'Country'
        codelist = iati.core.default.codelist(name, *standard_version_optional)

        assert isinstance(codelist, iati.core.Codelist)
        assert codelist.name == name
        for code in codelist.codes:
            assert isinstance(code, iati.core.Code)

    @pytest.mark.parametrize("name", iati.core.tests.utilities.generate_test_types(['str'], True))
    def test_default_codelist_invalid(self, name, standard_version_optional):
        """Check that trying to find a default Codelist with an invalid name raises an error."""
        with pytest.raises(ValueError) as excinfo:
            iati.core.default.codelist(name, *standard_version_optional)

        assert 'There is no default Codelist in version' in str(excinfo.value)

    def test_default_codelists_type(self, standard_version_optional):
        """Check that the default Codelists are of the correct type.

        Todo:
            Check internal values beyond the codelists being the correct type.
        """
        codelists = iati.core.default.codelists(*standard_version_optional)

        assert isinstance(codelists, dict)
        for _, codelist in codelists.items():
            assert isinstance(codelist, iati.core.Codelist)

    @pytest.mark.parametrize('version, expected_length', [
        ('2.02', 62),  # There are 38 embedded codelists at v2.02, plus 24 non-embedded codelists (which are valid for any version)
        ('2.01', 61),  # There are 37 embedded codelists at v2.01, plus 24 non-embedded codelists (which are valid for any version)
        ('1.05', 59),  # There are 35 embedded codelists at v1.05, plus 24 non-embedded codelists (which are valid for any version)
        ('1.04', 59)  # There are 35 embedded codelists at v1.04, plus 24 non-embedded codelists (which are valid for any version)
    ])
    def test_default_codelists_length(self, version, expected_length):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        codelists = iati.core.default.codelists(version)

        assert len(codelists) == expected_length

    def test_default_activity_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.activity_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == len(iati.core.constants.STANDARD_VERSIONS)
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.ActivitySchema)

    def test_default_organisation_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.organisation_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == len(iati.core.constants.STANDARD_VERSIONS)
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.OrganisationSchema)

    def test_default_schemas(self):
        """Check that the default Schemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        version = iati.core.constants.STANDARD_VERSION_LATEST
        schemas = iati.core.default.schemas()

        assert isinstance(schemas, dict)
        assert isinstance(schemas[version], dict)
        assert len(schemas[version]) == 2
        for schema in schemas[version].values():
            assert isinstance(schema, (iati.core.ActivitySchema, iati.core.OrganisationSchema))

    @pytest.mark.parametrize("invalid_name", iati.core.tests.utilities.generate_test_types([], True))
    def test_default_schema(self, invalid_name):
        """Check that an Error is raised when attempting to load a Schema name that does not exist."""
        with pytest.raises((ValueError, TypeError)):
            iati.core.default.schema(invalid_name)
