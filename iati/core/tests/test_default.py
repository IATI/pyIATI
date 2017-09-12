"""A module containing tests for the library representation of default values."""
import pytest
import iati.core.codelists
import iati.core.constants
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
from iati.core.tests.utilities import schema_ruleset


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

    @pytest.mark.parametrize("name", iati.core.tests.utilities.generate_test_types(['str'], True))
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

    def test_codelist_mapping_condition(self):
        """Check that the Codelist mapping file is being read correctly.

        Todo:
            Split into multiple tests.
        """
        mapping = iati.core.default.codelist_mapping()

        assert mapping['Sector'][0]['condition'] == "@vocabulary = '1' or not(@vocabulary)"
        assert mapping['Version'][0]['condition'] is None

    def test_codelist_mapping_xpath(self):
        """Check that the Codelist mapping file is being read correctly.

        Todo:
            Split into multiple tests.
        """
        mapping = iati.core.default.codelist_mapping()

        assert mapping['Version'][0]['xpath'] == '//iati-activities/@version'
        assert len(mapping['InvalidCodelistName']) == 0

    def test_default_ruleset(self):
        """Check that the default Ruleset is correct.

        Todo:
            Handle multiple versions.

            Check internal values beyond the Ruleset being the correct type.
        """
        ruleset = iati.core.default.ruleset()

        assert isinstance(ruleset, iati.core.Ruleset)

    def test_default_ruleset_validation_rules_valid(self, schema_ruleset):
        """Check that a fully valid IATI file does not raise any type of error (including rules/rulesets)."""
        data = iati.core.tests.utilities.load_as_dataset('valid_std_ruleset')
        result = iati.validator.full_validation(data, schema_ruleset)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert not result.contains_errors()

    @pytest.mark.parametrize("rule_error, invalid_dataset_name", [
        ('err-rule-at-least-one-conformance-fail', 'invalid_std_ruleset_missing_sector_element'),
        ('err-rule-date-order-conformance-fail', 'invalid_std_ruleset_bad_date_order'),
        ('err-rule-regex-matches-conformance-fail', 'invalid_std_ruleset_bad_identifier'),
        ('err-rule-sum-conformance-fail', 'invalid_std_ruleset_does_not_sum_100')
        # Note the Rules relating to 'dependent', 'no_more_than_one', 'regex_no_matches', 'startswith' and 'unique' are not used in the Standard Ruleset.
    ])
    def test_default_ruleset_validation_rules_invalid(self, schema_ruleset, rule_error, invalid_dataset_name):
        """Check that the expected rule error is detected when validating files containing invalid data for that rule.

        Todo:
            Consider whether this test should remove all warnings and assert that there is only the expected warning contained within the test file.
        """
        data = iati.core.tests.utilities.load_as_dataset(invalid_dataset_name)
        result = iati.validator.full_validation(data, schema_ruleset)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert not iati.validator.is_valid(data, schema_ruleset)
        assert result.contains_error_called(rule_error)

    def test_default_activity_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.activity_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == 1
        for _, schema in schemas.items():
            assert isinstance(schema, iati.core.ActivitySchema)

    def test_default_organisation_schemas(self):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schemas = iati.core.default.organisation_schemas()

        assert isinstance(schemas, dict)
        assert len(schemas) == 1
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
