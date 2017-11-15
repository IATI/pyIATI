"""A module containing tests for the library representation of default values."""
import pytest
import iati.codelists
import iati.constants
import iati.default
import iati.schemas
import iati.tests.utilities


class TestDefault(object):
    """A container for tests relating to Default data."""

    @pytest.mark.parametrize("invalid_version", iati.tests.utilities.generate_test_types(['none'], True))
    @pytest.mark.parametrize("func_to_check", [
        iati.default.get_default_version_if_none,
        iati.default.codelists,
        iati.default.codelist_mapping,
        iati.default.ruleset,
        iati.default.ruleset_schema,
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_invalid_version(self, invalid_version, func_to_check):
        """Check that an invalid version causes an error when obtaining default data."""
        with pytest.raises(ValueError):
            func_to_check(invalid_version)


class TestDefaultCodelists(object):
    """A container for tests relating to default Codelists."""

    @pytest.fixture
    def codelist_name(self):
        """Return the name of a valid Codelist."""
        return 'Country'

    @pytest.fixture
    def codelists_with_no_name_codes(self):
        """Return the names of Codelists where Codes do not have names."""
        return ['FileFormat', 'Version']

    @pytest.mark.parametrize("invalid_version", iati.tests.utilities.generate_test_types(['none'], True))
    def test_invalid_version_single_codelist(self, invalid_version, codelist_name):
        """Check that an invalid version causes an error when obtaining a single default Codelist.

        Note:
            This is a separate test since the function takes a parameter other than the `version`.

        """
        with pytest.raises(ValueError):
            iati.default.codelist(codelist_name, invalid_version)

    def test_default_codelist_valid_at_all_versions(self, codelist_name, standard_version_optional):
        """Check that a named default Codelist may be located.

        Todo:
            Check internal values beyond the codelists being the correct type.
        """
        codelist = iati.default.codelist(codelist_name, *standard_version_optional)

        assert isinstance(codelist, iati.Codelist)
        assert codelist.name == codelist_name
        for code in codelist.codes:
            assert isinstance(code, iati.Code)

    @pytest.mark.parametrize("version, codelist_name, expected_type", [
        ('1.04', 'AidTypeFlag', iati.Codelist),
        ('1.05', 'AidTypeFlag', iati.Codelist),
        ('2.01', 'AidTypeFlag', ValueError),
        ('2.02', 'AidTypeFlag', ValueError),
        ('1.04', 'BudgetStatus', ValueError),
        ('1.05', 'BudgetStatus', ValueError),
        ('2.01', 'BudgetStatus', ValueError),
        ('2.02', 'BudgetStatus', iati.Codelist)
    ])
    def test_default_codelist_valid_only_at_some_versions(self, codelist_name, version, expected_type):
        """Check that a codelist that is valid at some version/s is not valid in other versions.

        Example:
            AidTypeFlag was an embedded codelist in v1.04 and v1.05, but is not valid at any version after this.
            For example, BudgetStatus was added as an embedded codelist in v2.02, so is not valid prior to this.
        """
        try:  # Note pytest.raises() is not used here in order to keep this test flexible for parameterization.
            result = iati.default.codelist(codelist_name, version)
        except ValueError as excinfo:
            result = excinfo

        assert isinstance(result, expected_type)

    @pytest.mark.parametrize("name", iati.tests.utilities.generate_test_types(['str'], True))
    def test_default_codelist_invalid_at_all_versions(self, name, standard_version_optional):
        """Check that trying to find a default Codelist with an invalid name raises an error."""
        with pytest.raises(ValueError) as excinfo:
            iati.default.codelist(name, *standard_version_optional)

        assert 'There is no default Codelist in version' in str(excinfo.value)

    def test_default_codelists_type(self, codelist_lengths_by_version):
        """Check that the default Codelists are of the correct type.

        Todo:
            Switch from type-checking to behavior-checking, which is more Pythonic.
        """
        codelists = iati.default.codelists(codelist_lengths_by_version.version)

        assert isinstance(codelists, dict)
        assert len(codelists.values()) == codelist_lengths_by_version.expected_length
        for codelist in codelists.values():
            assert isinstance(codelist, iati.Codelist)
            for code in codelist.codes:
                assert isinstance(code, iati.Code)

    def test_default_codelists_codes_have_name(self, standard_version_optional, codelists_with_no_name_codes):
        """Check that Codelists with Codes that should have names do have names.

        Codes in a Codelist should have a name. This checks that default Codelists have names. A small number of Codelists are excluded because they are known not to have names.

        """
        codelists = iati.default.codelists(*standard_version_optional)
        relevant_codelists = [codelist for codelist in codelists.values() if codelist.name not in codelists_with_no_name_codes]

        for codelist in relevant_codelists:
            for code in codelist.codes:
                assert code.name != ''

    def test_default_codelists_no_name_codes_have_no_name(self, standard_version_optional, codelists_with_no_name_codes):
        """Check that Codelists with Codes that are known to have no name have no name.

        Ideally all Codes would have a name. There are a couple of Codelists where Codes do not. This test is intended to identify the point in time that names are added.

        """
        codelists = iati.default.codelists(*standard_version_optional)
        relevant_codelists = [codelist for codelist in codelists.values() if codelist.name in codelists_with_no_name_codes]

        for codelist in relevant_codelists:
            for code in codelist.codes:
                assert code.name == ''

    def test_codelist_mapping_condition(self):
        """Check that the Codelist mapping file is having conditions read.

        Todo:
            Split into multiple tests.

            Stop this being fixed to 2.02.

        """
        mapping = iati.default.codelist_mapping('2.02')

        assert mapping['Sector'][0]['condition'] == "@vocabulary = '1' or not(@vocabulary)"
        assert mapping['Version'][0]['condition'] is None

    def test_codelist_mapping_xpath(self, standard_version_optional):
        """Check that the Codelist mapping file is being read for both org and activity mappings.

        Todo:
            Split into multiple tests.

        """
        mapping = iati.default.codelist_mapping(*standard_version_optional)
        currency_xpaths = [currency_mapping['xpath'] for currency_mapping in mapping['Currency']]

        expected_xpaths = [
            '//iati-activity/@default-currency',
            '//iati-activity/budget/value/@currency',
            '//iati-activity/crs-add/loan-status/@currency',
            '//iati-activity/fss/forecast/@currency',
            '//iati-activity/planned-disbursement/value/@currency',
            '//iati-activity/transaction/value/@currency',
            '//iati-organisation/@default-currency',
            '//iati-organisation/total-budget/value/@currency',
            '//iati-organisation/recipient-org-budget/value/@currency',
            '//iati-organisation/recipient-country-budget/value/@currency'
        ]

        for xpath in expected_xpaths:
            assert xpath in currency_xpaths
        assert mapping['InvalidCodelistName'] == []

    def test_default_codelists_length(self, codelist_lengths_by_version):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        codelists = iati.default.codelists(codelist_lengths_by_version.version)

        assert len(codelists) == codelist_lengths_by_version.expected_length


class TestDefaultRulesets(object):
    """A container for tests relating to default Rulesets."""

    def test_default_ruleset(self, standard_version_optional):
        """Check that the default Ruleset is correct.

        Todo:
            Check internal values beyond the Ruleset being the correct type.

        """
        ruleset = iati.default.ruleset(*standard_version_optional)

        assert isinstance(ruleset, iati.Ruleset)

    def test_default_ruleset_validation_rules_valid(self, schema_ruleset):
        """Check that a fully valid IATI file does not raise any type of error (including rules/rulesets).

        Todo:
            Stop this being fixed to 2.02.

        """
        data = iati.tests.resources.load_as_dataset('valid_std_ruleset', '2.02')
        result = iati.validator.full_validation(data, schema_ruleset)

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert not result.contains_errors()

    @pytest.mark.parametrize("rule_error, invalid_dataset_name, info_text", [
        (
            'err-rule-at-least-one-conformance-fail',
            'ruleset-std/invalid_std_ruleset_missing_sector_element',
            'At least one of `sector` or `transaction/sector` must be present within each `//iati-activity`.'
        ),
        (
            'err-rule-date-order-conformance-fail',
            'ruleset-std/invalid_std_ruleset_bad_date_order',
            '`activity-date[@type=\'1\']/@iso-date` must be chronologically before `activity-date[@type=\'3\']/@iso-date` within each `//iati-activity`.'
        ),
        (
            'err-rule-regex-matches-conformance-fail',
            'ruleset-std/invalid_std_ruleset_bad_identifier',
            'Each instance of `reporting-org/@ref` and `iati-identifier` and `participating-org/@ref` and `transaction/provider-org/@ref` and `transaction/receiver-org/@ref` within each `//iati-activity` must match the regular expression `[^\\/\\&\\|\\?]+`.'  # noqa: disable=E501 # pylint: disable=line-too-long
        ),
        (
            'err-rule-sum-conformance-fail',
            'ruleset-std/invalid_std_ruleset_does_not_sum_100',
            'Within each `//iati-activity`, the sum of values matched at `recipient-country/@percentage` and `recipient-region/@percentage` must be `100`.'
        )
        # Note the Rules relating to 'dependent', 'no_more_than_one', 'regex_no_matches', 'startswith' and 'unique' are not used in the Standard Ruleset.
    ])
    def test_default_ruleset_validation_rules_invalid(self, schema_ruleset, rule_error, invalid_dataset_name, info_text):
        """Check that the expected rule error is detected when validating files containing invalid data for that rule.

        Note:
            The fixed strings being checked here may be a tad annoying to maintain.
            `test_rule_string_output_general` and `test_rule_string_output_specific` in `test_rulesets.py` do something related for Rules. As such, something more generic may work better in the future.

        Todo:
            Consider whether this test should remove all warnings and assert that there is only the expected warning contained within the test file.

            Check that the expected missing elements appear the the help text for the given element.

            Stop this being fixed to 2.02.

        """
        data = iati.tests.resources.load_as_dataset(invalid_dataset_name, '2.02')
        result = iati.validator.full_validation(data, schema_ruleset)
        errors_for_rule_error = result.get_errors_or_warnings_by_name(rule_error)
        errors_for_ruleset = result.get_errors_or_warnings_by_name('err-ruleset-conformance-fail')

        assert iati.validator.is_xml(data.xml_str)
        assert iati.validator.is_iati_xml(data, schema_ruleset)
        assert not iati.validator.is_valid(data, schema_ruleset)
        assert len(errors_for_rule_error) == 1
        assert len(errors_for_ruleset) == 1
        assert info_text in errors_for_rule_error[0].info


class TestDefaultSchemas(object):
    """A container for tests relating to default Schemas."""

    def test_default_activity_schemas(self, standard_version_optional):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schema = iati.default.activity_schema(*standard_version_optional)

        assert isinstance(schema, iati.ActivitySchema)

    def test_default_organisation_schemas(self, standard_version_optional):
        """Check that the default ActivitySchemas are correct.

        Todo:
            Check internal values beyond the schemas being the correct type.
        """
        schema = iati.default.organisation_schema(*standard_version_optional)

        assert isinstance(schema, iati.OrganisationSchema)

    @pytest.mark.parametrize("population_status", [[], [True]])
    @pytest.mark.parametrize("schema_func", [
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_default_schemas_populated(self, population_status, schema_func, codelist_lengths_by_version):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        schema = schema_func(codelist_lengths_by_version.version, *population_status)

        assert len(schema.codelists) == codelist_lengths_by_version.expected_length
        assert len(schema.rulesets) == 1

    @pytest.mark.parametrize("schema_func", [
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_default_schemas_unpopulated(self, schema_func, standard_version_mandatory):
        """Check that the default Codelists for each version contain the expected number of Codelists."""
        schema = schema_func(standard_version_mandatory[0], False)

        assert schema.codelists == set()
        assert schema.rulesets == set()


class TestDefaultModifications(object):
    """A container for tests relating to the ability to modify defaults."""

    @pytest.fixture
    def codelist_name(self):
        """Return the name of a Codelist that exists at all versions of the Standard."""
        return 'Country'

    @pytest.fixture
    def codelist(self, codelist_name):
        """Return a default Codelist that is part of the IATI Standard."""
        return iati.default.codelist(codelist_name)

    @pytest.fixture
    def codelist_non_default(self):
        """Return a Codelist that is not part of the IATI Standard."""
        return iati.Codelist('custom codelist')

    @pytest.fixture
    def new_code(self):
        """Return a Code object that has not been added to a Codelist."""
        return iati.Code('new code value', 'new code name')

    def test_default_codelist_modification(self, codelist_name, new_code, standard_version_optional):
        """Check that a default Codelist cannot be modified by adding Codes to returned lists."""
        default_codelist = iati.default.codelist(codelist_name, *standard_version_optional)
        base_default_codelist_length = len(default_codelist.codes)

        default_codelist.codes.add(new_code)
        unmodified_codelist = iati.default.codelist(codelist_name, *standard_version_optional)

        assert len(default_codelist.codes) == base_default_codelist_length + 1
        assert len(unmodified_codelist.codes) == base_default_codelist_length

    def test_default_codelists_modification(self, codelist_name, new_code, standard_version_optional):
        """Check that default Codelists cannot be modified by adding Codes to returned lists with default parameters."""
        default_codelists = iati.default.codelists(*standard_version_optional)
        codelist_of_interest = default_codelists[codelist_name]
        base_default_codelist_length = len(codelist_of_interest.codes)

        codelist_of_interest.codes.add(new_code)
        unmodified_codelists = iati.default.codelists(*standard_version_optional)
        unmodified_codelist_of_interest = unmodified_codelists[codelist_name]

        assert len(codelist_of_interest.codes) == base_default_codelist_length + 1
        assert len(unmodified_codelist_of_interest.codes) == base_default_codelist_length

    @pytest.mark.parametrize("default_call", [
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_default_x_schema_modification_unpopulated(self, default_call, codelist, standard_version_mandatory):
        """Check that unpopulated default Schemas cannot be modified.

        Note:
            Implementation is by attempting to add a Codelist to the Schema.

        """
        default_schema = default_call(standard_version_mandatory[0], False)
        base_codelist_count = len(default_schema.codelists)

        default_schema.codelists.add(codelist)
        unmodified_schema = default_call(standard_version_mandatory[0], False)

        assert len(default_schema.codelists) == base_codelist_count + 1
        assert len(unmodified_schema.codelists) == base_codelist_count

    @pytest.mark.parametrize("default_call", [
        iati.default.activity_schema,
        iati.default.organisation_schema
    ])
    def test_default_x_schema_modification_populated(self, default_call, codelist_non_default, standard_version_mandatory):
        """Check that populated default Schemas cannot be modified.

        Note:
            Implementation is by attempting to add a Codelist to the Schema.

        """
        default_schema = default_call(standard_version_mandatory[0], True)
        base_codelist_count = len(default_schema.codelists)

        default_schema.codelists.add(codelist_non_default)
        unmodified_schema = default_call(standard_version_mandatory[0], True)

        assert len(default_schema.codelists) == base_codelist_count + 1
        assert len(unmodified_schema.codelists) == base_codelist_count
