"""A module containing tests for the library representation of default values."""
import pytest
import iati.core.codelists
import iati.core.constants
import iati.core.default
import iati.core.schemas
from iati.core.tests.utilities import codelist_lengths_by_version, standard_version_mandatory, standard_version_optional


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelist_valid_at_all_versions(self, standard_version_optional):
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

    @pytest.mark.parametrize("version, codelist_name, expected_type", [
        ('1.04', 'AidTypeFlag', iati.core.Codelist),
        ('1.05', 'AidTypeFlag', iati.core.Codelist),
        ('2.01', 'AidTypeFlag', ValueError),
        ('2.02', 'AidTypeFlag', ValueError),
        ('1.04', 'BudgetStatus', ValueError),
        ('1.05', 'BudgetStatus', ValueError),
        ('2.01', 'BudgetStatus', ValueError),
        ('2.02', 'BudgetStatus', iati.core.Codelist)
    ])
    def test_default_codelist_valid_only_at_some_versions(self, codelist_name, version, expected_type):
        """Check that a codelist that is valid at some version/s is not valid in other versions.
        For example:
            AidTypeFlag was an embedded codelist in v1.04 and v1.05, but is not valid at any version after this.
            For example, BudgetStatus was added as an embedded codelist in v2.02, so is not valid prior to this.
        """
        try:  # Note pytest.raises() is not used here in order to keep this test flexible for parameterization.
            result = iati.core.default.codelist(codelist_name, version)
        except ValueError as excinfo:
            result = excinfo

        assert isinstance(result, expected_type)

    @pytest.mark.parametrize("name", iati.core.tests.utilities.generate_test_types(['str'], True))
    def test_default_codelist_invalid_at_all_versions(self, name, standard_version_optional):
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

    def test_default_codelists_length(self, codelist_lengths_by_version):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        codelists = iati.core.default.codelists(codelist_lengths_by_version.version)

        assert len(codelists) == codelist_lengths_by_version.expected_length

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


class TestDefaultModifications(object):
    """A container for tests relating to the ability to modify defaults."""


    @pytest.fixture
    def codelist_name(self):
        """Return the name of a Codelist that exists at all versions of the Standard."""
        return 'Country'

    @pytest.fixture
    def codelist(self, codelist_name):
        """Return a Codelist."""
        return iati.core.default.codelist(codelist_name)

    @pytest.fixture
    def new_code(self):
        """Return a Code object that has not been added to a Codelist."""
        return iati.core.Code('new code value', 'new code name')

    def test_default_codelist_modification(self, codelist_name, new_code, standard_version_optional):
        """Check that a default Codelist cannot be modified by adding Codes to returned lists."""
        default_codelist = iati.core.default.codelist(codelist_name, *standard_version_optional)
        base_default_codelist_length = len(default_codelist.codes)

        default_codelist.codes.add(new_code)
        unmodified_codelist = iati.core.default.codelist(codelist_name, *standard_version_optional)

        assert len(default_codelist.codes) == base_default_codelist_length + 1
        assert len(unmodified_codelist.codes) == base_default_codelist_length

    def test_default_codelists_modification(self, codelist_name, new_code, standard_version_optional):
        """Check that default Codelists cannot be modified by adding Codes to returned lists with default parameters."""
        default_codelists = iati.core.default.codelists(*standard_version_optional)
        codelist_of_interest = default_codelists[codelist_name]
        base_default_codelist_length = len(codelist_of_interest.codes)

        codelist_of_interest.codes.add(new_code)
        unmodified_codelists = iati.core.default.codelists(*standard_version_optional)
        unmodified_codelist_of_interest = unmodified_codelists[codelist_name]

        assert len(codelist_of_interest.codes) == base_default_codelist_length + 1
        assert len(unmodified_codelist_of_interest.codes) == base_default_codelist_length

    @pytest.mark.parametrize("default_call", [
        iati.core.default.activity_schemas,
        iati.core.default.organisation_schemas
    ])
    def test_default_x_schema_modification(self, default_call, codelist, standard_version_mandatory):
        """Check that the default Schemas cannot be modified.

        Note:
            Implementation is by attempting to add a Codelist to the Schema.

        """
        default_schema = default_call()[standard_version_mandatory[0]]
        base_codelist_count = len(default_schema.codelists)

        default_schema.codelists.add(codelist)
        unmodified_schema = default_call()[standard_version_mandatory[0]]

        assert len(default_schema.codelists) == base_codelist_count + 1
        assert len(unmodified_schema.codelists) == base_codelist_count

    @pytest.mark.parametrize("schema_name", [
        'iati-activities-schema',
        'iati-organisations-schema'
    ])
    def test_default_schema_modification(self, schema_name, standard_version_optional, codelist):
        """Check that the default Schemas cannot be modified when called individually.

        Note:
            Implementation is by attempting to add a Codelist to the Schema.

        """
        default_schema = iati.core.default.schema(schema_name, *standard_version_optional)
        base_codelist_count = len(default_schema.codelists)

        default_schema.codelists.add(codelist)
        unmodified_schema = iati.core.default.schema(schema_name, *standard_version_optional)

        assert len(default_schema.codelists) == base_codelist_count + 1
        assert len(unmodified_schema.codelists) == base_codelist_count
