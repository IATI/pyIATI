"""A module containing tests for the library representation of Rulesets."""
import pytest
import iati.core.default
import iati.core.rulesets
import iati.core.resources
import iati.core.tests.utilities


class TestRuleset(object):
    """A container for tests relating to Rulesets."""

    def test_ruleset_init_no_parameters(self):
        """Check that a Ruleset cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            iati.core.Ruleset()

    def test_ruleset_init_ruleset_str_valid(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": []}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert ruleset.rules == set()

    @pytest.mark.parametrize("not_a_ruleset", iati.core.tests.utilities.find_parameter_by_type(['str', 'bytearray'], False))
    def test_ruleset_init_ruleset_str_not_str(self, not_a_ruleset):
        """Check that a Ruleset cannot be created when given at least one Rule in a non-string format."""
        with pytest.raises(TypeError):
            iati.core.Ruleset(not_a_ruleset)

    # @pytest.mark.skip(reason="Bytearrays cause multiple types of errors. This is confusing. Probs due to the stupid null byte at the start of one of the sample bytearrays. Grr! Argh!")
    @pytest.mark.parametrize("byte_array", iati.core.tests.utilities.find_parameter_by_type(['bytearray']))
    def test_ruleset_init_ruleset_str_bytearray(self, byte_array):
        """Check that a Ruleset cannot be created when given at least one Rule in a bytearray format."""
        with pytest.raises(ValueError):
            iati.core.Ruleset(byte_array)

    def test_ruleset_init_ruleset_str_invalid(self):
        """Check that a Ruleset cannot be created when given a string that is not a Ruleset."""
        not_a_ruleset_str = 'this is not a ruleset: it is a cat'

        with pytest.raises(ValueError):
            iati.core.Ruleset(not_a_ruleset_str)

    def test_ruleset_init_ruleset_1_rule(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with one Rule."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 1
        assert isinstance(list(ruleset.rules)[0], iati.core.Rule)
        assert isinstance(list(ruleset.rules)[0], iati.core.rulesets.RuleAtLeastOne)

    def test_ruleset_init_ruleset_1_rule_invalid_type(self):
        """Check that a Ruleset raises a KeyError when given a JSON Ruleset in string format with an invalid rule_type key."""
        ruleset_str = '{"CONTEXT": {"invalid_rule_type": {"cases": [{"paths": ["test_path"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_2_rules_single_case(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules under a single case."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}, {"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
            assert isinstance(rule, iati.core.rulesets.RuleAtLeastOne)

    def test_ruleset_init_ruleset_multiple_cases(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of different types, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.rulesets.RuleAtLeastOne)]) == 1
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.rulesets.RuleNoMoreThanOne)]) == 1

    def test_ruleset_init_ruleset_duplicate_types(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_duplicate_contexts(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"DUPLICATE_CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "DUPLICATE_CONTEXT": {"no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.core.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_multiple_contexts(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of the same type, each under a different context."""
        ruleset_str = '{"CONTEXT_1": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "CONTEXT_2": {"atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
            assert isinstance(rule, iati.core.rulesets.RuleAtLeastOne)


class TestRule(object):
    """A container for tests relating to Rules."""

    def test_rule_class_cannot_be_instantiated_directly_without_name(self):
        """Check that Rule itself cannot be directly instantiated."""
        xpath_base = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(AttributeError):
            iati.core.Rule(xpath_base, case)

    def test_rule_class_cannot_be_instantiated_directly_with_name(self):
        """Check that Rule itself cannot be directly instantiated with a Rule name."""
        name = 'atleast_one'
        xpath_base = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(TypeError):
            iati.core.Rule(name, xpath_base, case)


class TestRuleSubclasses(object):
    """A container for tests relating to all Rule subclasses."""

    rule_constructors = list(map(iati.core.rulesets.locate_constructor_for_rule_type, iati.core.rulesets._VALID_RULE_TYPES))
    """A list of constructors for the various types of Rule."""

    @pytest.mark.parametrize("rule_constructor", rule_constructors)
    def test_rule_init_no_parameters(self, rule_constructor):
        """Check that a Rule cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            rule_constructor()

    @pytest.mark.parametrize("rule_constructor", rule_constructors)
    @pytest.mark.parametrize("xpath_base", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_rule_init_invalid_xpath_base(self, rule_constructor, xpath_base):
        """Check that a Rule cannot be created when xpath_base is not a string.

        Todo:
            Ensure the case is valid - an empty dictionary isn't.
        """
        case = dict()

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, case)

    @pytest.mark.parametrize("rule_constructor", rule_constructors)
    @pytest.mark.parametrize("case", iati.core.tests.utilities.find_parameter_by_type(['mapping'], False))
    def test_rule_init_invalid_case(self, rule_constructor, case):
        """Check that a Rule cannot be created when case is not a dictionary."""
        xpath_base = 'an xpath'

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, case)

    @pytest.mark.parametrize("rule_constructor", rule_constructors)
    def test_rule_init_invalid_case_property(self, rule_constructor):
        """Check that a Rule cannot be created when a case has a property that is not permitted."""
        xpath_base = 'an xpath'
        case = {'thisis_an_invalidkey': ['this_is_a_value']}

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, case)


class RuleSubclassTestBase(object):
    """A base class for Rule subclass tests."""

    @pytest.fixture
    def basic_rule(self, rule_constructor, valid_case):
        """Instantiate a basic Rule subclass."""
        xpath_base = 'an xpath'
        return rule_constructor(xpath_base, valid_case)

    @pytest.fixture
    def rule_constructor(self, rule_type):
        """Return the constructor for the current Rule type."""
        return iati.core.rulesets.locate_constructor_for_rule_type(rule_type)

    def test_rule_init_valid_parameter_types(self, basic_rule):
        """Check that Rule subclasses can be instantiated with valid parameter types."""
        assert isinstance(basic_rule, iati.core.Rule)

    def test_rule_attributes_from_case(self, basic_rule):
        """Check that a Rule subclass has case attributes set."""
        required_attributes = basic_rule._required_case_attributes(basic_rule._ruleset_schema_section())
        for attrib in required_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(basic_rule, attrib)

    def test_rule_name(self, basic_rule, rule_type):
        """Check that a Rule subclass has the expected name."""
        assert basic_rule.name == rule_type

    def test_rule_paths(self, basic_rule):
        """Check that a Rule subclass has the expected paths."""
        # Exclude rules with no `paths` attribute.
        if 'paths' in dir(basic_rule):
            for path in basic_rule.paths:
                assert path.startswith(basic_rule.xpath_base)

    def test_rule_invalid_case(self, rule_constructor, invalid_case):
        """Check that a rule cannot be instantiated when the case is invalid.

        Todo:
            Add tests with empty path AND empty xpath_base.
        """
        xpath_base = 'an xpath'

        with pytest.raises(ValueError):
            rule_constructor(xpath_base, invalid_case)

    def test_is_valid_for(self, valid_dataset, rule):
        """Check that a given rule returns the expected result when given a dataset.

        Todo:
            Maybe too much of a shortcut as can't fully pass until all implementations complete. Possibly the wrong abstraction in the long-term.
        """
        assert rule.is_valid_for(valid_dataset)

    def test_is_invalid_for(self, invalid_dataset, rule):
        """Check that a given rule returns the expected result when given a dataset.

        Todo:
            Maybe too much of a shortcut as can't fully pass until all implementations complete. Possibly the wrong abstraction in the long-term.
        """
        assert not rule.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_data", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_is_valid_for_raises_error_on_non_permitted_argument(self, rule, junk_data):
        """Check that a given rule returns expected error when passed an argument that is not a dataset."""
        with pytest.raises(AttributeError):
            rule.is_valid_for(junk_data)

    def test_what_happens_with_an_etree(self, rule):
        """Check that an error is raised if an etree is given as an argument instead of a dataset."""
        with pytest.raises(AttributeError):
            rule.is_valid_for(iati.core.resources.load_as_tree(iati.core.resources.get_test_data_path('valid_atleastone')))


class TestRuleAtLeastOne(RuleSubclassTestBase):
    """A container for tests relating to RuleAtLeastOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'atleast_one'

    @pytest.fixture(params=[
        {'paths': ['']},  # empty path
        {'paths': ['path_1']},  # single path
        {'paths': ['path_1', 'path_2']},  # multiple paths
        {'paths': ['path_1', 'path_1']}  # duplicate paths
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': []},  # empty path array
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_VALID

    @pytest.fixture(params=[
        {'paths': ['element_that_only_occurs_once']},
        {'paths': ['element_that_only_occurs_once', 'element_that_occurs_twice']}
    ])
    def rule(self, request):
        """Instantiate RuleAtLeastOne."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleAtLeastOne(xpath_base, request.param)


class TestRuleDateOrder(RuleSubclassTestBase):
    """A container for tests relating to RuleDateOrder."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'date_order'

    @pytest.fixture(params=[
        {'less': 'start-xpath', 'more': 'end-xpath'},  # both `less` and `more` present
        {'less': 'start-xpath', 'more': 'NOW'},  # `more` as NOW
        {'less': 'NOW', 'more': 'end-xpath'},  # `less` as NOW
        {'less': 'NOW', 'more': 'NOW'},  # both `less` and `more` as NOW
        {'less': 'start-xpath', 'more': 'start-xpath'},  # both `less` and `more` as same xpath
        {'less': '2017-07-26T13:19:05.493Z', 'more': 'end-xpath'},  # `less` is a string-formatted date
        {'less': 'start-xpath', 'more': '2017-07-26T13:19:05.493Z'}  # `more` is a string-formatted date
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'less': 'start'},  # missing required attribute - `more`
        {'more': 'end'},  # missing required attribute - `less`
        {'less': 1501075031590, 'more': 'end-xpath'},  # `less` is a numeric value
        {'less': 'start-xpath', 'more': 1501075031590},  # `more` is a numeric value
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_VALID

    @pytest.fixture(params=[
        {"less": "planned-disbursement/period-start/@iso-date", "more": "planned-disbursement/period-end/@iso-date"}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleDateOrder(xpath_base, request.param)

    def test_rule_paths_less(self, basic_rule):
        """Check that the `less` value has been combined with the `xpath_base` where required."""
        if basic_rule.less.endswith(basic_rule.special_case):
            assert basic_rule.less == basic_rule.special_case
        else:
            assert basic_rule.less.startswith(basic_rule.xpath_base)

    def test_rule_paths_more(self, basic_rule):
        """Check that the `more` value has been combined with the `xpath_base` where required."""
        if basic_rule.more.endswith(basic_rule.special_case):
            assert basic_rule.more == basic_rule.special_case
        else:
            assert basic_rule.more.startswith(basic_rule.xpath_base)


class TestRuleDependent(RuleSubclassTestBase):
    """A container for tests relating to RuleDependent."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'dependent'

    @pytest.fixture(params=[
        {'paths': ['']},  # empty path
        {'paths': ['path_1']},  # single path
        {'paths': ['path_1', 'path_2']},  # multiple paths
        {'paths': ['path_1', 'path_1']}  # duplicate paths
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': []},  # empty path array
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_VALID

    @pytest.fixture(params=[
        {"paths": ["transaction/provider-org", "location/point"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleDependent(xpath_base, request.param)


class TestRuleNoMoreThanOne(RuleSubclassTestBase):
    """A container for tests relating to RuleNoMoreThanOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'no_more_than_one'

    @pytest.fixture(params=[
        {'paths': ['']},  # empty path
        {'paths': ['path_1']},  # single path
        {'paths': ['path_1', 'path_2']},  # multiple paths
        {'paths': ['path_1', 'path_1']}  # duplicate paths
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': []},  # empty path array
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_VALID

    @pytest.fixture(params=[
        {"paths": ["element_that_only_occurs_once"]},
        {"paths": ["element_that_only_occurs_once", "another_element_that_only_occurs_once"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleNoMoreThanOne(xpath_base, request.param)


class TestRuleRegexMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexMatches."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'regex_matches'

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': ['']},  # empty path with regex
        {'regex': 'some regex', 'paths': ['path_1']},  # single path with regex
        {'regex': 'some regex', 'paths': ['path_1', 'path_2']},  # multiple paths with regex
        {'regex': 'some regex', 'paths': ['path_1', 'path_1']},  # duplicate paths with regex
        {'regex': '', 'paths': ['path_1']}  # single path with regex
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': []},  # empty path array
        {'regex': 'some regex', 'paths': 'path_1'},  # non-array `paths`
        {'regex': 'some regex', 'paths': [3]},  # non-string value in path array
        {'regex': 'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'regex': 'some regex'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
        {'regex': '[', 'paths': ['path_1']},  # provided string not a valid regex
        {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_VALID

    @pytest.fixture(params=[
        {"regex": r"[^\/\\&\\|\\?]+", "paths": ["iati-identifier"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleRegexMatches(xpath_base, request.param)


class TestRuleRegexNoMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexNoMatches."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'regex_no_matches'

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': ['']},  # empty path with regex
        {'regex': 'some regex', 'paths': ['path_1']},  # single path with regex
        {'regex': 'some regex', 'paths': ['path_1', 'path_2']},  # multiple paths with regex
        {'regex': 'some regex', 'paths': ['path_1', 'path_1']},  # duplicate paths with regex
        {'regex': '', 'paths': ['path_1']}  # single path with regex
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': []},  # empty path array
        {'regex': 'some regex', 'paths': 'path_1'},  # non-array `paths`
        {'regex': 'some regex', 'paths': [3]},  # non-string value in path array
        {'regex': 'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'regex': 'some regex'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
        {'regex': '[', 'paths': ['path_1']},  # provided string not a valid regex
        {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_VALID

    @pytest.fixture(params=[
        {"regex": r"[^\/\\&\\|\\?]+", "paths": ["iati-identifier"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleRegexNoMatches(xpath_base, request.param)


class TestRuleStartsWith(RuleSubclassTestBase):
    """A container for tests relating to RuleStartsWith."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'startswith'

    @pytest.fixture(params=[
        {'start': 'prefix-xpath', 'paths': ['']},  # empty path with prefix
        {'start': 'prefix-xpath', 'paths': ['path_1']},  # single path with prefix
        {'start': 'prefix-xpath', 'paths': ['path_1', 'path_2']},  # multiple paths with prefix
        {'start': 'prefix-xpath', 'paths': ['path_1', 'path_1']},  # duplicate paths with prefix
        {'start': '', 'paths': ['path_1']}  # single path with prefix
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'start': 'prefix-xpath', 'paths': []},  # empty path array
        {'start': 'prefix-xpath', 'paths': 'path_1'},  # non-array `paths`
        {'start': 'prefix-xpath', 'paths': [3]},  # non-string value in path array
        {'start': 'prefix-xpath', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'start': 3, 'paths': ['path_1']},  # provided prefix xpath not a string
        {'start': 'prefix-xpath'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `start`
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_VALID

    @pytest.fixture(params=[
        {"start": "reporting-org/@ref", "paths": ["iati-identifier"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleStartsWith(xpath_base, request.param)

    def test_rule_paths_start(self, basic_rule):
        """Check that the `start` value has been combined with the `xpath_base`."""
        assert basic_rule.start.startswith(basic_rule.xpath_base)


class TestRuleSum(RuleSubclassTestBase):
    """A container for tests relating to RuleSum."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'sum'

    @pytest.fixture(params=[
        {'paths': [''], 'sum': 3},  # empty path with sum
        {'paths': ['path_1'], 'sum': 3},  # single path with sum
        {'paths': ['path_1', 'path_2'], 'sum': 3},  # multiple paths with sum
        {'paths': ['path_1', 'path_1'], 'sum': 3},  # duplicate paths with sum
        {'paths': ['path_1'], 'sum': -1000},  # negative sum
        {'paths': ['path_1'], 'sum': 101},  # sum greater than standard percentage limit
        {'paths': ['path_1'], 'sum': 15.5},  # decimal sum
        {'paths': ['path_1'], 'sum': 0},  # zero sum
        {'paths': ['path_1'], 'sum': 10**100},  # big sum
        {'paths': ['path_1'], 'sum': -10**100},  # tiny sum
        {'paths': ['path_1'], 'sum': 2.99792458e6}  # exponential sum
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': [], 'sum': 3},  # empty path array
        {'paths': 'path_1', 'sum': 3},  # non-array `paths`
        {'paths': [3], 'sum': 3},  # non-string value in path array
        {'paths': ['path_1', 3], 'sum': 3},  # mixed string and non-string value in path array
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `sum`
        {'sum': 100},  # missing required attribute - `paths`
        {},  # empty dictionary
        {'paths': ['path_1'], 'sum': '3'}  # sum is a string representation of a number
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_VALID

    @pytest.fixture(params=[
        {"paths": ["recipient-country/@percentage", "recipient-region/@percentage"], "sum": 100}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleSum(xpath_base, request.param)


class TestRuleUnique(RuleSubclassTestBase):
    """A container for tests relating to RuleUnique."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'unique'

    @pytest.fixture(params=[
        {'paths': ['']},  # empty path
        {'paths': ['path_1']},  # single path
        {'paths': ['path_1', 'path_2']},  # multiple paths
        {'paths': ['path_1', 'path_1']}  # duplicate paths
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': []},  # empty path array
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {}  # empty dictionary
    ])
    def invalid_case(self, request):
        """Non-permitted case for this rule."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_VALID

    @pytest.fixture(params=[
        {"paths": ["iati-identifier"]},
        {"paths": ["iati-identifier", "other_unique_element"]}
    ])
    def rule(self, request):
        """Ruleset contains only this Rule."""
        xpath_base = '//root_element'
        return iati.core.rulesets.RuleUnique(xpath_base, request.param)
