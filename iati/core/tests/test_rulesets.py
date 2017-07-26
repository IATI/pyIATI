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

    @pytest.mark.skip(reason="Bytearrays cause multiple types of errors. This is confusing. Probs due to the stupid null byte at the start of one of the sample bytearrays. Grr! Argh!")
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
        """Check that a Rule cannot be created when xpath_base is not a string."""
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
    def basic_rule(self, rule_type, valid_case):
        """Instantiate a basic Rule subclass."""
        xpath_base = 'an xpath'
        rule_constructor = iati.core.rulesets.locate_constructor_for_rule_type(rule_type)
        return rule_constructor(xpath_base, valid_case)

    @pytest.fixture
    def invalid_case_rule(self, rule_type):
        """Invalid instantiation of a Rule subclass."""
        rule_constructor = iati.core.rulesets.locate_constructor_for_rule_type(rule_type)
        return rule_constructor

    def test_rule_init_valid_parameter_types(self, basic_rule):
        """Check that Rule subclasses can be instantiated with valid parameter types."""
        assert isinstance(basic_rule, iati.core.Rule)

    def test_rule_name(self, basic_rule, rule_type):
        """Check that a Rule subclass has the expected name."""
        assert basic_rule.name == rule_type

    def test_rule_missing_required_case_properties(self, invalid_case_rule, invalid_cases):
        """Check that a rule cannot be instantiated without the required case properties."""
        xpath_base = 'an xpath'

        with pytest.raises(ValueError):
            invalid_case_rule(xpath_base, invalid_cases)

    @pytest.mark.skip(reason="Not implemented for some subclasses")
    def test_is_valid_for(self, invalid_data_tree, valid_data_tree, this_rule_only_ruleset):
        """Check that the 'atleast_one' rule returns the expected result when given a dataset.

        Todo:
            Maybe too much of a shortcut as can't fully pass until all implementations complete. Probably the wrong abstraction in the long-term.
        """
        for rule in this_rule_only_ruleset.rules:
            assert not rule.is_valid_for(invalid_data_tree)
            assert rule.is_valid_for(valid_data_tree)


class TestRuleNoMoreThanOne(RuleSubclassTestBase):
    """A container for tests relating to RuleNoMoreThanOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'no_more_than_one'

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param

    @pytest.fixture
    def invalid_data_tree(self):
        """Invalid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_NOMORETHANONE_RULE_INVALID

    @pytest.fixture
    def valid_data_tree(self):
        """Return valid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_NOMORETHANONE_RULE_VALID

    @pytest.fixture
    def this_rule_only_ruleset(self):
        """Ruleset contains only this Rule."""
        ruleset_str = iati.core.tests.utilities.NOMORETHANONE_RULESET_STR
        return iati.core.Ruleset(ruleset_str)


class TestRuleAtLeastOne(RuleSubclassTestBase):
    """A container for tests relating to RuleAtLeastOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'atleast_one'

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param

    @pytest.fixture
    def invalid_data_tree(self):
        """Invalid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_ATLEASTONE_RULE_INVALID

    @pytest.fixture
    def valid_data_tree(self):
        """Return valid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_ATLEASTONE_RULE_VALID

    @pytest.fixture
    def this_rule_only_ruleset(self):
        """Ruleset contains only this Rule."""
        ruleset_str = iati.core.tests.utilities.ATLEASTONE_RULESET_STR
        return iati.core.Ruleset(ruleset_str)


class TestRuleDependent(RuleSubclassTestBase):
    """A container for tests relating to RuleDependent."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'dependent'

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    # If this rule is checking for dependent paths then surely it's invalid to pass in only one path property?
    @pytest.fixture(params=[
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param


class TestRuleSum(RuleSubclassTestBase):
    """A container for tests relating to RuleSum."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'sum'

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2'], 'sum': 3}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2']},
        {'sum': 100},
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param


class TestRuleDateOrder(RuleSubclassTestBase):
    """A container for tests relating to RuleDateOrder."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'date_order'

    @pytest.fixture(params=[
        {'less': 'start', 'more': 'end'}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'less': 'start'},
        {'more': 'end'},
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param


class TestRuleRegexMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexMatches."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'regex_matches'

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'regex': 'some regex'},
        {'paths': ['path_1', 'path_2']},
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param

    @pytest.fixture
    def invalid_data_tree(self):
        """Invalid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_REGEXMATCHES_RULE_INVALID

    @pytest.fixture
    def valid_data_tree(self):
        """Return valid dataset etree for this Rule."""
        return iati.core.tests.utilities.DATASET_TREE_FOR_REGEXMATCHES_RULE_VALID

    @pytest.fixture
    def this_rule_only_ruleset(self):
        """Ruleset contains only this Rule."""
        ruleset_str = iati.core.tests.utilities.REGEXMATCHES_RULESET_STR
        return iati.core.Ruleset(ruleset_str)


class TestRuleRegexNoMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexNoMatches."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'regex_no_matches'

    @pytest.fixture(params=[
        {'regex': 'some regex', 'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'regex': 'some regex'},
        {'paths': ['path_1', 'path_2']},
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param


class TestRuleStartsWith(RuleSubclassTestBase):
    """A container for tests relating to RuleStartsWith."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'startswith'

    @pytest.fixture(params=[
        {'start': 'a string', 'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {'start': 'a string'},
        {'paths': ['path_1', 'path_2']},
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param


class TestRuleUnique(RuleSubclassTestBase):
    """A container for tests relating to RuleUnique."""

    @pytest.fixture
    def rule_type(self):
        """Type of rule."""
        return 'unique'

    @pytest.fixture(params=[
        {'paths': ['path_1', 'path_2']}
    ])
    def valid_case(self, request):
        """Permitted case for this rule."""
        return request.param

    @pytest.fixture(params=[
        {}
    ])
    def invalid_cases(self, request):
        """Non-permitted cases for this rule."""
        return request.param
