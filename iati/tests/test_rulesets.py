"""A module containing tests for the library representation of Rulesets.

Todo:
    Check all tests are still necessary/relevant.
    Condense tests for individual Rules.
    Try to normalise Rule arrays for extraction.

"""
# pylint: disable=protected-access,too-many-lines
from copy import deepcopy
import pytest
import iati.default
import iati.rulesets
import iati.resources
import iati.tests.utilities


class RulesetFixtures(object):
    """A base class for fixtures to use in Ruleset tests."""

    empty_init_config = [
        '{"CONTEXT": {"atleast_one": {"cases": []}}}',  # JSON string that has no Rules
        ' ',  # whitespace only
        '',  # empty string
        None  # none
    ]

    @pytest.fixture(params=empty_init_config)
    def ruleset_empty(self, request):
        """Return an empty Ruleset."""
        return iati.Ruleset(request.param)

    one_rule_init_config = [
        '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path"]}]}}}'
    ]

    @pytest.fixture(params=one_rule_init_config)
    def ruleset_one_rule(self, request):
        """Return a Ruleset containing one Rule."""
        return iati.Ruleset(request.param)

    multiple_rules_one_context_init_config = [  # pylint: disable=invalid-name
        '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}, {"paths": ["test_path_2"]}]}}}',  # same type of Rule
        '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}',  # different types of Rule, different case info
        '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "no_more_than_one": {"cases": [{"paths": ["test_path_1"]}]}}}',  # different types of Rule, same case info
    ]

    @pytest.fixture(params=multiple_rules_one_context_init_config)
    def ruleset_multiple_rules_one_context(self, request):
        """Return a Ruleset containing multiple Rules. All Rules are in the same context."""
        return iati.Ruleset(request.param)

    multiple_rules_multiple_contexts_init_config = [  # pylint: disable=invalid-name
        '{"CONTEXT_1": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "CONTEXT_2": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}}',  # same case in each context
        '{"CONTEXT_1": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "CONTEXT_2": {"atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'  # different case in each context
    ]

    @pytest.fixture(params=multiple_rules_multiple_contexts_init_config)
    def ruleset_multiple_rules_multiple_contexts(self, request):
        """Return a Ruleset containing multiple Rules. The Rules are spread across multiple contexts."""
        return iati.Ruleset(request.param)

    @pytest.fixture(params=one_rule_init_config + multiple_rules_one_context_init_config + multiple_rules_multiple_contexts_init_config)
    def ruleset_non_empty(self, request):
        """Return a Ruleset that contains at least one Rule."""
        return iati.Ruleset(request.param)

    @pytest.fixture(params=empty_init_config + one_rule_init_config + multiple_rules_one_context_init_config + multiple_rules_multiple_contexts_init_config)
    def ruleset(self, request):
        """Return a Ruleset."""
        return iati.Ruleset(request.param)


class TestRulesetInitialisation(RulesetFixtures):
    """A container for tests relating to Ruleset initialisation."""

    def test_ruleset_init_empty(self, ruleset_empty):
        """Check that an empty Ruleset can be created."""
        ruleset = ruleset_empty

        assert isinstance(ruleset, iati.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert ruleset.rules == set()

    @pytest.mark.parametrize("not_a_ruleset", [
        '{"xpath": "string"}',
        '{"xpath": 1}',
        '{"xpath": 1.1}',
        '{"xpath": null}',
        '{"xpath": true}',
        '{"xpath": ["array", 1, true]}',
    ] + iati.tests.utilities.generate_test_types(['str', 'bytearray', 'none'], True))
    def test_ruleset_init_ruleset_str_not_str(self, not_a_ruleset):
        """Check that a Ruleset cannot be created when given a string that does not conform to the Ruleset Schema."""
        with pytest.raises(ValueError):
            iati.Ruleset(not_a_ruleset)

    @pytest.mark.parametrize("byte_array", iati.tests.utilities.generate_test_types(['bytearray']))
    def test_ruleset_init_ruleset_str_bytearray(self, byte_array):
        """Check that a Ruleset cannot be created when given at least one Rule in a bytearray format."""
        with pytest.raises(ValueError):
            iati.Ruleset(byte_array)

    def test_ruleset_init_ruleset_str_invalid(self):
        """Check that a Ruleset cannot be created when given a string that is not a Ruleset."""
        not_a_ruleset_str = 'This is not a ruleset: It is a cat. Meow, meow.'

        with pytest.raises(ValueError):
            iati.Ruleset(not_a_ruleset_str)

    def test_ruleset_init_ruleset_1_rule(self, ruleset_one_rule):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with one Rule."""
        ruleset = ruleset_one_rule

        assert isinstance(ruleset, iati.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 1
        assert isinstance(list(ruleset.rules)[0], iati.Rule)
        assert isinstance(list(ruleset.rules)[0], iati.RuleAtLeastOne)

    def test_ruleset_init_ruleset_1_rule_invalid_type(self):
        """Check that a Ruleset raises a KeyError when given a JSON Ruleset in string format with an invalid rule_type key."""
        ruleset_str = '{"CONTEXT": {"invalid_rule_type": {"cases": [{"paths": ["test_path"]}]}}}'

        with pytest.raises(ValueError):
            iati.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_multiple_rules_single_context(self, ruleset_multiple_rules_one_context):  # pylint: disable=invalid-name
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with multiple Rules under a single context."""
        ruleset = ruleset_multiple_rules_one_context

        assert isinstance(ruleset, iati.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.Rule)

    def test_ruleset_init_ruleset_duplicate_types(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "atleast_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_duplicate_contexts(self):
        """Check that a Ruleset raises a ValueError when given a JSON Ruleset in string format with two Rules of the same type, each under the same context."""
        ruleset_str = '{"DUPLICATE_CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}}, "DUPLICATE_CONTEXT": {"no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        with pytest.raises(ValueError):
            iati.Ruleset(ruleset_str)

    def test_ruleset_init_ruleset_multiple_contexts(self, ruleset_multiple_rules_multiple_contexts):  # pylint: disable=invalid-name
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of the same type, each under a different context."""
        ruleset = ruleset_multiple_rules_multiple_contexts

        assert isinstance(ruleset, iati.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.Rule)
            assert isinstance(rule, iati.RuleAtLeastOne)


class TestRulesetValidityChecks(RulesetFixtures):
    """A container for tests relating to checking whether a Dataset is valid for a Ruleset."""

    def test_ruleset_is_valid_for_valid_dataset(self):
        """Check that a Dataset can be validated against the Standard Ruleset.

        Todo:
            Stop this being fixed to 2.02.

        """
        ruleset = iati.tests.utilities.RULESET_FOR_TESTING
        valid_dataset = iati.tests.resources.load_as_dataset('valid_std_ruleset', '2.02')

        assert ruleset.is_valid_for(valid_dataset)

    @pytest.mark.parametrize("invalid_dataset", [
        iati.tests.resources.load_as_dataset('ruleset-std/invalid_std_ruleset_bad_date_order', '2.02'),
        iati.tests.resources.load_as_dataset('ruleset-std/invalid_std_ruleset_bad_identifier', '2.02'),
        iati.tests.resources.load_as_dataset('ruleset-std/invalid_std_ruleset_does_not_sum_100', '2.02'),
        iati.tests.resources.load_as_dataset('ruleset-std/invalid_std_ruleset_missing_sector_element', '2.02')
    ])
    def test_ruleset_is_invalid_for_invalid_dataset(self, invalid_dataset):
        """Check that a Dataset can be invalidated against the Standard Ruleset.

        Todo:
            Stop this being fixed to 2.02.

        """
        ruleset = iati.tests.utilities.RULESET_FOR_TESTING
        assert not ruleset.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("dataset_name, rule_type, case", [
        ('ruleset/invalid_format_dateorder', 'date_order', {'less': 'element1', 'more': 'element2'}),
        ('ruleset/invalid_startswith', 'startswith', {'start': 'duplicateprefix', 'paths': ['element12']}),
        ('ruleset/invalid_sum', 'sum', {'paths': ['element42'], 'sum': 50}),
    ])
    def test_ruleset_is_invalid_for_valueerror(self, dataset_name, rule_type, case):
        """Check that `ValueError`s are correctly handled when checking a Ruleset.

        Rulesets should absorb them and return `False` rather than passing them on to the caller.

        """
        invalid_dataset = iati.tests.resources.load_as_dataset(dataset_name)
        rule_constructor = iati.rulesets.constructor_for_rule_type(rule_type)
        rule = rule_constructor('//root_element', case)
        ruleset = iati.Ruleset('')
        ruleset.rules.add(rule)

        assert not ruleset.is_valid_for(invalid_dataset)


class TestRulesetEquality(RulesetFixtures):
    """A container for tests relating to checking the equality of Rulesets."""

    @pytest.fixture
    def rule(self):
        """Return a Rule."""
        return iati.RuleAtLeastOne('TestRulesetEqualityCONTEXT', {"paths": ["test_path"]})

    def test_ruleset_same_object_equal(self, ruleset, cmp_func_equal_val_and_hash):
        """Check that a Rule is deemed to be equal with itself."""
        assert cmp_func_equal_val_and_hash(ruleset, ruleset)

    def test_ruleset_same_diff_object_equal(self, ruleset, cmp_func_equal_val, cmp_func_different_hash):
        """Check that two instances of the same Ruleset are deemed to be equal."""
        ruleset_copy = deepcopy(ruleset)

        assert cmp_func_equal_val(ruleset, ruleset_copy)
        assert cmp_func_different_hash(ruleset, ruleset_copy)

    def test_ruleset_diff_num_rules_not_equal(self, ruleset, rule, cmp_func_different_val_and_hash):
        """Check that two different Rulesets are not deemed to be equal.

        One Ruleset contains a Rule that the other does not, but they are otherwise identical.
        """
        ruleset_copy = deepcopy(ruleset)
        ruleset_copy.rules.add(rule)

        assert cmp_func_different_val_and_hash(ruleset, ruleset_copy)

    def test_ruleset_diff_rule_not_equal(self, ruleset_non_empty, cmp_func_different_val_and_hash):
        """Check that two different Rulesets are not deemed to be equal.

        One contained Rule differs between the Rulesets, but they are otherwise identical.
        """
        ruleset = ruleset_non_empty
        ruleset_copy = deepcopy(ruleset)
        rule = ruleset_copy.rules.pop()
        rule._name = rule._name + 'with-a-difference'
        ruleset_copy.rules.add(rule)

        assert cmp_func_different_val_and_hash(ruleset, ruleset_copy)


class TestRule(object):
    """A container for tests relating to Rules."""

    def test_rule_class_cannot_be_instantiated_directly_without_name(self):
        """Check that Rule itself cannot be directly instantiated."""
        context = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(AttributeError):
            iati.Rule(context, case)

    def test_rule_class_cannot_be_instantiated_directly_with_name(self):
        """Check that Rule itself cannot be directly instantiated with a Rule name."""
        name = 'atleast_one'
        context = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(TypeError):
            iati.Rule(name, context, case)  # pylint: disable=too-many-function-args


class TestRuleSubclasses(object):
    """A container for tests relating to all Rule subclasses."""

    @pytest.fixture(params=[
        iati.rulesets.constructor_for_rule_type(rule_type) for rule_type in iati.rulesets._VALID_RULE_TYPES
    ])
    def rule_constructor(self, request):
        """Return constructor for the current type of Rule.

        Note:
            Differs from fixture of same name in RuleSubclassTestBase as specifies rule_type by _VALID_RULE_TYPES rather than via specific TestRuleSubclass.

        """
        return request.param

    def test_rule_init_no_parameters(self, rule_constructor):
        """Check that a Rule cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            rule_constructor()

    @pytest.mark.parametrize("xpath_base", iati.tests.utilities.generate_test_types(['str'], True))
    def test_rule_init_invalid_xpath_base(self, rule_constructor, xpath_base):
        """Check that a Rule cannot be created when xpath_base is not a string.

        Todo:
            Ensure the case is valid - an empty dictionary isn't.
        """
        case = dict()

        with pytest.raises(TypeError):
            rule_constructor(xpath_base, case)

    @pytest.mark.parametrize("case", iati.tests.utilities.generate_test_types(['mapping'], True))
    def test_rule_init_invalid_case(self, rule_constructor, case):
        """Check that a Rule cannot be created when case is not a dictionary."""
        context = 'an xpath'

        with pytest.raises(ValueError):
            rule_constructor(context, case)

    def test_rule_init_invalid_case_property(self, rule_constructor):
        """Check that a Rule cannot be created when a case has a property that is not permitted."""
        context = 'an xpath'
        case = {'thisis_an_invalidkey': ['this_is_a_value']}

        with pytest.raises(ValueError):
            rule_constructor(context, case)


class RuleSubclassFixtures(object):
    """A base class for fixtures to use in Rule subclass tests."""

    @pytest.fixture
    def valid_single_context(self):
        """Return valid context with a single match."""
        return '//root_element'

    @pytest.fixture
    def valid_multiple_context(self):
        """Return a valid context with multiple matches."""
        return '//nest'

    @pytest.fixture
    def non_existent_context(self):
        """Return an XPath for a context that does not exist."""
        return '//non-existent-context'

    @pytest.fixture(params=[
        'count(condition)>0',
        'condition'
    ])
    def condition_is_true_valid(self, validating_case, request):
        """Return a case with optional condition that evaluates to `True` for a valid dataset."""
        condition_validating_case = deepcopy(validating_case)
        condition_validating_case['condition'] = request.param
        return condition_validating_case

    @pytest.fixture(params=[
        'count(condition)>0',
        'condition'
    ])
    def condition_is_true_invalid(self, invalidating_case, request):
        """Return a case with optional condition that evaluates to `True` for an invalid dataset."""
        condition_invalidating_case = deepcopy(invalidating_case)
        condition_invalidating_case['condition'] = request.param
        return condition_invalidating_case

    @pytest.fixture(params=[
        'count(condition)<1',
        'nocondition'
    ])
    def condition_is_false_valid(self, validating_case, request):
        """Return a case with an optional condition that evaluates to False for a valid dataset."""
        condition_validating_case = deepcopy(validating_case)
        condition_validating_case['condition'] = request.param
        return condition_validating_case

    @pytest.fixture()
    def rule(self, rule_constructor, valid_single_context, single_instantiating_case):
        """A single instance of a Rule subclass."""
        return rule_constructor(valid_single_context, single_instantiating_case)

    @pytest.fixture
    def rule_instantiating(self, rule_constructor, instantiating_case, valid_single_context):
        """Rule subclass that instantiates but is not used for validation testing."""
        return rule_constructor(valid_single_context, instantiating_case)

    @pytest.fixture
    def rule_valid(self, rule_constructor, validating_case, valid_single_context):
        """Rule for checking the `is_valid_for` function against a relevant valid Dataset."""
        return rule_constructor(valid_single_context, validating_case)

    @pytest.fixture
    def rule_invalid(self, rule_constructor, invalidating_case, valid_single_context):
        """Rule for checking the `is_valid_for` function against a relevant invalid Dataset."""
        return rule_constructor(valid_single_context, invalidating_case)

    @pytest.fixture
    def rule_constructor(self, rule_type):
        """Return current Rule type.

        Note:
            Differs from fixture of same name in TestRuleSubclass as specifies rule_type via specific TestRuleSubclass fixture.

        """
        return iati.rulesets.constructor_for_rule_type(rule_type)

    @pytest.fixture
    def valid_condition_rule(self, rule_constructor, valid_single_context, condition_is_true_valid):
        """Return a Rule with a `condition`."""
        return rule_constructor(valid_single_context, condition_is_true_valid)

    @pytest.fixture
    def invalid_condition_rule(self, rule_constructor, valid_single_context, condition_is_true_invalid):
        """Return a Rule with a `condition`."""
        return rule_constructor(valid_single_context, condition_is_true_invalid)


class RuleSubclassTestsGeneral(RuleSubclassFixtures):  # pylint: disable=too-many-public-methods
    """A container for general tests for Rule subclasses.

    Todo:
        Where `rule_instantiating` is used, determine whether changing to `rule` would reduce the coverage of the test.

        Test and ensure dynamically-created attributes (`less`, `more`, `paths`, etc) are not writable after instantiation.

    """

    def test_rule_init_valid_parameter_types(self, rule_instantiating):
        """Check that Rule subclasses can be instantiated with valid parameter types."""
        assert isinstance(rule_instantiating, iati.Rule)

    def test_rule_init_raises_error_on_empty_context(self, rule_constructor, instantiating_case):
        """Check that a Rule cannot be instantiated when the `context` is an empty string."""
        invalid_context = ''
        with pytest.raises(ValueError):
            rule_constructor(invalid_context, instantiating_case)

    def test_rule_attributes_from_case(self, rule_instantiating):
        """Check that a Rule subclass has mandatory case attributes set."""
        required_attributes = rule_instantiating._case_attributes(rule_instantiating._ruleset_schema_section())
        for attrib in required_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(rule_instantiating, attrib)

    def test_optional_rule_attributes_from_case(self, rule_constructor, valid_single_context, condition_is_true_valid):
        """Check that a Rule subclass has optional case attributes set."""
        rule = rule_constructor(valid_single_context, condition_is_true_valid)
        optional_attributes = rule._case_attributes(rule._ruleset_schema_section(), False)
        for attrib in optional_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(rule, attrib)

    def test_rule_name(self, rule_instantiating, rule_type):
        """Check that a Rule subclass has the expected name."""
        assert rule_instantiating.name == rule_type

    def test_rule_name_cannot_be_set(self, rule):
        """Check that a Rule subclass cannot have its name changed after instantiation."""
        with pytest.raises(AttributeError):
            rule.name = 'a new name'

    def test_rule_context_cannot_be_set(self, rule):
        """Check that a Rule subclass cannot have its context changed after instantiation."""
        with pytest.raises(AttributeError):
            rule.context = 'a-new-context'

    def test_rule_string_output_general(self, rule_instantiating):
        """Check that the string format of the Rule has been customised and variables formatted."""
        assert 'iati.rulesets' not in str(rule_instantiating)
        assert ' object at ' not in str(rule_instantiating)
        assert 'self' not in str(rule_instantiating)
        assert '{0}' not in str(rule_instantiating)
        assert 'This is a Rule' not in str(rule_instantiating)

    @pytest.mark.parametrize("context", iati.tests.utilities.generate_test_types(['str'], True))
    def test_rule_init_invalid_context(self, rule_constructor, context, instantiating_case):
        """Check that a Rule subclass cannot be created when context is not a string."""
        with pytest.raises(TypeError):
            rule_constructor(context, instantiating_case)

    def test_rule_invalid_case(self, rule_constructor, uninstantiating_case):
        """Check that a Rule cannot be instantiated when the case is not permitted."""
        context = 'an xpath'
        with pytest.raises(ValueError):
            rule_constructor(context, uninstantiating_case)

    def test_is_valid_for(self, valid_dataset, rule_valid):
        """Check that a given Rule returns the expected result when given Dataset."""
        assert rule_valid.is_valid_for(valid_dataset)

    def test_is_invalid_for(self, invalid_dataset, rule_invalid):
        """Check that a given Rule returns the expected result when given a Dataset."""
        assert not rule_invalid.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_data", iati.tests.utilities.generate_test_types([], True))
    def test_is_valid_for_raises_error_on_non_permitted_argument(self, rule_instantiating, junk_data):
        """Check that a given Rule returns expected error when passed an argument that is not a Dataset."""
        with pytest.raises(TypeError):
            rule_instantiating.is_valid_for(junk_data)

    def test_is_valid_for_raises_error_when_passed_an_etree(self, rule_instantiating):
        """Check that an error is raised if an etree is given as an argument instead of a Dataset.

        Todo:
            Use more generic Dataset.

        """
        with pytest.raises(TypeError):
            rule_instantiating.is_valid_for(iati.utilities.load_as_tree(iati.tests.resources.get_test_data_path('ruleset/valid_atleastone')))

    def test_multiple_valid_context_matches_is_valid_for(self, valid_multiple_context, valid_nest_case, rule_constructor, valid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(valid_multiple_context, valid_nest_case)
        assert rule.is_valid_for(valid_dataset)

    def test_multiple_valid_context_matches_is_invalid_for(self, valid_multiple_context, invalid_nest_case, rule_constructor, invalid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(valid_multiple_context, invalid_nest_case)
        assert not rule.is_valid_for(invalid_dataset)

    def test_non_existent_context_is_valid_for(self, non_existent_context, valid_nest_case, rule_constructor, valid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(non_existent_context, valid_nest_case)
        assert rule.is_valid_for(valid_dataset) is None

    def test_non_existent_context_is_invalid_for(self, non_existent_context, invalid_nest_case, rule_constructor, invalid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(non_existent_context, invalid_nest_case)
        assert rule.is_valid_for(invalid_dataset) is None

    def test_condition_case_is_True_for_valid_dataset(self, valid_condition_rule, valid_dataset):
        """Check that if a condition is `True`, the rule returns None which is considered equivalent to skipping."""
        assert valid_condition_rule.is_valid_for(valid_dataset) is None

    def test_condition_case_is_True_for_invalid_dataset(self, invalid_condition_rule, invalid_dataset):
        """Check that if a condition is `True`, the rule returns None which is considered equivalent to skipping."""
        assert invalid_condition_rule.is_valid_for(invalid_dataset) is None

    def test_condition_case_is_False_for_valid_dataset(self, rule_constructor, valid_single_context, condition_is_false_valid, valid_dataset):
        """Check that if a condition is `False`, the rule validates normally."""
        rule = rule_constructor(valid_single_context, condition_is_false_valid)
        assert rule.is_valid_for(valid_dataset)

    def test_condition_case_is_False_for_invalid_dataset(self, invalid_condition_rule, invalid_dataset):
        """Check that if a condition is `False`, the rule validates normally.

        Note:
            Using an invalid dataset so expecting Rules to evaluate to `False`.

        """
        assert not invalid_condition_rule.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_condition", [''] + iati.tests.utilities.generate_test_types(['str'], True))
    def test_uninstantiating_condition_case(self, rule_constructor, valid_single_context, validating_case, junk_condition):
        """Check that a non-permitted condition case will not instantiate."""
        junk_condition_case = deepcopy(validating_case)
        junk_condition_case['condition'] = junk_condition
        with pytest.raises(ValueError):
            rule_constructor(valid_single_context, junk_condition_case)


class RuleSubclassEquality(RuleSubclassFixtures):
    """A container for tests relating to checking the equality of Rule subclasses."""

    def test_rule_same_object_equal(self, rule, cmp_func_equal_val_and_hash):
        """Check that a Rule is deemed to be equal with itself."""
        assert cmp_func_equal_val_and_hash(rule, rule)

    def test_rule_same_diff_object_equal(self, rule, cmp_func_equal_val_and_hash):
        """Check that two instances of the same Rule are deemed to be equal."""
        rule_copy = deepcopy(rule)

        assert cmp_func_equal_val_and_hash(rule, rule_copy)

    def test_rule_diff_name_not_equal(self, rule, cmp_func_different_val_and_hash):
        """Check that two different Rules are not deemed to be equal.

        The two Rules have different names, but are otherwise identical.
        """
        rule_copy = deepcopy(rule)
        rule_copy._name = rule.name + 'with-a-difference'

        assert cmp_func_different_val_and_hash(rule, rule_copy)

    def test_rule_diff_context_not_equal(self, rule, cmp_func_different_val_and_hash):
        """Check that two different Rules are not deemed to be equal.

        The two Rules have different contexts, but are otherwise identical.
        """
        rule_copy = deepcopy(rule)
        rule_copy._context = rule.context + 'with-a-difference'

        assert cmp_func_different_val_and_hash(rule, rule_copy)


class RuleSubclassTestBase(RuleSubclassTestsGeneral, RuleSubclassEquality):
    """A base class for Rule subclass tests.

    This allows particular types of Rule to inherit from a single class, while allowing for logical separation of blocks of tests.
    """

    pass


class TestRuleAtLeastOne(RuleSubclassTestBase):
    """A container for tests relating to RuleAtLeastOne."""

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'atleast_one'

    all_valid_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element6/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element7/@attribute', 'element8/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element9/@attribute', 'element9/@attribute']},
        {'paths': ['element11']}  # multiple identitcal elements
    ]

    uninstantiating_cases = [
        {'paths': []},  # empty path array
        {'paths': ['']},  # path is an empty string
        {'paths': 'element'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['element', 3]},  # mixed string and non-string values in path array
        {'paths': ['element/@attribute', 3]},
        {},  # empty dictionary
        {'paths': {'element'}},  # dictionary paths
        {'paths': {'element/@attribute'}},
        {'paths': 'element'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {}  # empty dictionary
    ]

    invalidating_cases = [
        {'paths': ['element1']},  # single path, no matches
        {'paths': ['element9/@attribute']},
        {'paths': ['element7', 'element8']},  # multiple paths, both expected matches missing
        {'paths': ['element13/@attribute', 'element14/@attribute']}
    ]

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted case for validating an XML dataset against RuleAtLeastOne."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleAtLeastOne."""
        return request.param

    @pytest.fixture
    def valid_nest_case(self):
        """Non-permitted case for validating an XML dataset against RuleAtLeastOne in nested context."""
        return {'paths': ['element5', 'element10']}

    @pytest.fixture
    def invalid_nest_case(self):
        """Non-permitted case for validating an XML dataset against RuleAtLeastOne in nested context."""
        return {'paths': ['element2', 'element10/@attribute']}

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_atleastone')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_atleastone')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must be present' in str(rule_instantiating)


class TestRuleDateOrder(RuleSubclassTestBase):
    """A container for tests relating to RuleDateOrder.

    Note:
        RuleDateOrder is special and is implemented in a weird way. It is not a happy duck. Therefore, it has special cases that will instantiate but are not valid, which is not the case with other Rules.

    Todo:
        Test implementation of functionality to ignore function call if `less` or `more` do not return dates.

    """

    instatiating_cases = [
        {'less': 'element', 'more': 'element'},  # both `less` and `more` duplicate xpath
        {'less': 'element/@attribute', 'more': 'element/@attribute'},
        {'less': '2017-07-26T13:19:05.493Z', 'more': 'element'},  # `less` is a string-formatted date
        {'less': '2017-07-26T13:19:05.493Z', 'more': 'element/@attribute'},
        {'less': 'element', 'more': '2017-07-26T13:19:05.493Z'},  # `more` is a string-formatted date
        {'less': 'element/@attribute', 'more': '2017-07-26T13:19:05.493Z'},
        {'less': 'NOW', 'more': 'NOW'}  # both `less` and `more` as NOW
    ]

    validating_cases = [
        {'less': 'element1', 'more': 'element2'},  # correct date order
        {'less': 'element11/@attribute', 'more': 'element12/@attribute'},
        {'less': 'element3', 'more': 'NOW'},  # `more` is NOW
        {'less': 'element13/@attribute', 'more': 'NOW'},
        {'less': 'NOW', 'more': 'element4'},  # `less` is NOW
        {'less': 'NOW', 'more': 'element14/@attribute'},
        {'less': 'element5', 'more': 'element6'},  # multiple identical `less` values
        {'less': 'element15/@attribute', 'more': 'element16/@attribute'},
        {'less': 'element7', 'more': 'element8'},  # multiple identical `more` values
        {'less': 'element17/@attribute', 'more': 'element18/@attribute'},
        {'less': '//element9', 'more': '//element10'},  # nested data
        {'less': '//element19/@attribute', 'more': '//element20/@attribute'},
        {'less': 'element21', 'more': 'element22'},  # positive timezone value
        {'less': 'element29/@attribute', 'more': 'element30/@attribute'},
        {'less': 'element23', 'more': 'element24'},  # negative timezone value
        {'less': 'element31/@attribute', 'more': 'element32/@attribute'},
        {'less': 'element25', 'more': 'element26'},  # timezone not on the hour
        {'less': 'element33/@attribute', 'more': 'element34/@attribute'},
        {'less': 'element27', 'more': 'element28'},  # UTC timezone
        {'less': 'element35/@attribute', 'more': 'element36/@attribute'},
        {'less': 'nOw', 'more': 'noW'},  # not special case, should treat as regular path value
        {'less': 'now/@attribute', 'more': 'Now/@attribute'},
        {'less': 'element37', 'more': 'element38'},  # multiple identical elements
        {'less': 'element47', 'more': 'element48'},  # dates have identical values
        {'less': 'element49/@attribute', 'more': 'element50/@attribute'},
        {'less': 'element51', 'more': 'element51'},  # `less` and `more` reference the same date
        {'less': 'element52/@attribute', 'more': 'element52/@attribute'}
    ]

    all_valid_cases = instatiating_cases + validating_cases

    uninstantiating_cases = [
        {'less': 'start'},  # missing required attribute - `more`
        {'more': 'end'},  # missing required attribute - `less`
        {'less': '', 'more': ''},  # path case is empty string
        {'less': 1501075031590, 'more': 'end-xpath'},  # `less` is not a string
        {'less': 'start-xpath', 'more': 1501075031590},  # `more` is not a string
        {},  # empty dictionary
        {'less': ['start']},  # less is a list
        {'more': ['end']},  # more is a list
    ]

    invalidating_cases = [
        {'less': 'element1', 'more': 'element2'},  # dates not in chronological order
        {'less': 'element14/@attribute', 'more': 'element15/@attribute'},
        {'less': 'NOW', 'more': 'element5'},  # `more` is chronologically before NOW
        {'less': 'NOW', 'more': 'element18/@attribute'},
        {'less': 'element6', 'more': 'NOW'},  # `less` is chronologically after NOW
        {'less': 'element19/@attribute', 'more': 'NOW'},
        {'less': '//element7', 'more': '//element8'},  # nested dates not in chronological order
        {'less': '//element20/@attribute', 'more': '//element21/@attribute'},
        {'less': 'element10', 'more': 'element11'},  # multiple identical `less` dates that are chronologically after `more`
        {'less': 'element23/@attribute', 'more': 'element24/@attribute'},
        {'less': 'element12', 'more': 'element13'},  # multiple identical `more` dates that are chronologically before `less`
        {'less': 'element25/@attribute', 'more': 'element26/@attribute'},
        {'less': 'element27', 'more': 'element28'},  # multiple identical elements in incorrect order
        {'less': 'element29', 'more': 'xpath-that-does-not-exist'},  # the xpath for more does not exist
        {'less': 'xpath-that-does-not-exist', 'more': 'element29'}  # the xpath for less does not exist
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'date_order'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=validating_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleDateOrder."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleDateOrder."""
        return request.param

    @pytest.fixture(params=[
        {'less': '//element9', 'more': '//element10'},
        {'less': '//element19/@attribute', 'more': '//element20/@attribute'}
    ])
    def valid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleDateOrder in nested context."""
        return request.param

    @pytest.fixture(params=[
        {'less': '//element7', 'more': '//element8'},
        {'less': '//element20/@attribute', 'more': '//element21/@attribute'}
    ])
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleDateOrder in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for instatiating this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_dateorder')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_dateorder')

    @pytest.mark.parametrize("case", [
        {'less': 'element1', 'more': 'element2'},  # Euro-date format
        {'less': 'element17/@attribute', 'more': 'element18/@attribute'},
        {'less': 'element3', 'more': 'element4'},  # USA-date format
        {'less': 'element19/@attribute', 'more': 'element20/@attribute'},
        {'less': 'element5', 'more': 'element6'},  # month is given as text
        {'less': 'element21/@attribute', 'more': 'element22/@attribute'},
        {'less': 'element7', 'more': 'element8'},  # year given in shortened format
        {'less': 'element23/@attribute', 'more': 'element24/@attribute'},
        {'less': 'element9', 'more': 'element10'},  # leading characters included
        {'less': 'element25/@attribute', 'more': 'element26/@attribute'},
        {'less': 'element11', 'more': 'element12'},  # non-permitted trailing characters
        {'less': 'element27/@attribute', 'more': 'element28/@attribute'},
        {'less': 'element13', 'more': 'element14'},  # leading whitespace
        {'less': 'element29/@attribute', 'more': 'element30/@attribute'},
        {'less': 'element15', 'more': 'element16'},  # trailing whitespace
        {'less': 'element31/@attribute', 'more': 'element32/@attribute'},
        {'less': 'element33', 'more': 'element34'},  # timezone not zero-padded
        {'less': 'element35/@attribute', 'more': 'element36/@attribute'},
        {'less': 'element37', 'more': 'element38'},  # non-permitted leading timezone character
        {'less': 'element39/@attribute', 'more': 'element40/@attribute'},
        {'less': 'element41', 'more': 'element42'},  # multiple identical elements but non-duplicated values
        {'less': 'element43', 'more': 'element44'},  # UNIX timestamp format
        {'less': 'element45/@attribute', 'more': 'element46/@attribute'},
        {'less': 'element47', 'more': 'element48'},  # All text date format
        {'less': 'element49/@attribute', 'more': 'element50/@attribute'},
        {'less': 'element51', 'more': 'element52'},  # missing day
        {'less': 'element53', 'more': 'element54'},  # day not zero-padded
        {'less': 'element55', 'more': 'element56'}  # month not zero-padded
    ])
    def test_incorrect_date_format_raises_error(self, valid_single_context, case, rule_constructor):
        """Check that a dataset with dates in an incorrect format raise expected error."""
        rule = rule_constructor(valid_single_context, case)
        with pytest.raises(ValueError):
            rule.is_valid_for(iati.tests.resources.load_as_dataset('ruleset/invalid_format_dateorder'))

    @pytest.mark.parametrize("case", [
        {'less': 'element39', 'more': 'element40'},  # `less` date missing
        {'less': 'element43', 'more': 'element44'},
        {'less': 'element41', 'more': 'element42'},  # `more` date missing
        {'less': 'element45', 'more': 'element46'}
    ])
    def test_is_valid_for_returns_None(self, valid_single_context, case, rule_constructor, valid_dataset):
        """Check that None is returned when expected date not found."""
        rule = rule_constructor(valid_single_context, case)
        assert rule.is_valid_for(valid_dataset) is None

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_instantiating) for needle in ['must be chronologically', 'in the future', 'in the past'])


class TestRuleDependent(RuleSubclassTestBase):
    """A container for tests relating to RuleDependent."""

    all_valid_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element7/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element8/@attribute', 'element9/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element10/@attribute', 'element10/@attribute']},
        {'paths': ['element13', 'element14']}  # duplicate elements
    ]

    uninstantiating_cases = [
        {'paths': []},  # empty path array
        {'paths': ['']},  # path is an empty string
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {},  # empty dictionary
        {'paths': {'path_1'}}  # path value is dictionary instead of list
    ]

    invalidating_cases = [
        {'paths': ['element1', 'element2', 'element3']},  # dependent element missing
        {'paths': ['element4/@attribute', 'element5/@attribute', 'element6/@attribute']},  # dependent attribute missing
        {'paths': ['element10', 'element11']}  # dependent element of duplicate element missing
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'dependent'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleDependent."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleDependent."""
        return request.param

    @pytest.fixture(params=[
        {'paths': ['./element5', './element6']},
        {'paths': ['./element11/@attribute', './element12/@attribute']}

    ])
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleDependent in nested context."""
        return request.param

    @pytest.fixture(params=[
        {'paths': ['./element7', './element8']},
        {'paths': ['./element9/@attribute', './element10/@attribute']},
        {'paths': ['./element15', './element16']}
    ])
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleDependent in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for instatiating this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_dependent')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_dependent')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_instantiating) for needle in ['must all exist', 'always True'])


class TestRuleNoMoreThanOne(RuleSubclassTestBase):
    """A container for tests relating to RuleNoMoreThanOne."""

    all_valid_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element5/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element6/@attribute', 'element7/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element8/@attribute', 'element8/@attribute']}
    ]

    uninstantiating_cases = [
        {'paths': []},  # empty path array
        {'paths': ['']},  # path is an empty string
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {},  # empty dictionary
        {'paths': {'path_1'}}  # dictionary paths
    ]

    invalidating_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element7/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths, multiple of each
        {'paths': ['element8/@attribute', 'element9/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element10/@attribute', 'element10/@attribute']},
        {'paths': ['element5', 'element6']},  # one path valid, another invalid
        {'paths': ['element11/@attribute', 'element12/@attribute']},
        {'paths': ['element15', 'element16']},  # multiple paths, one of each
        {'paths': ['element17/@attribute', 'element18/@attribute']}  # multiple paths, one of each
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'no_more_than_one'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleNoMoreThanOne."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted casesd for validating an XML dataset against RuleNoMoreThanOne."""
        return request.param

    @pytest.fixture
    def valid_nest_case(self):
        """Permitted case for validating an XML dataset against RuleNoMoreThanOne in nested context."""
        return {'paths': ['element9', 'element10/@attribute']}

    @pytest.fixture
    def invalid_nest_case(self):
        """Non-permitted case for validating an XML dataset against RuleNoMoreThanOne in nested context."""
        return {'paths': ['element13', 'element14/@attribute']}

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_nomorethanone')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_nomorethanone')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_instantiating) for needle in ['zero or one', 'no more than one'])


class TestRuleRegexMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexMatches."""

    all_valid_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']},  # duplicate element
        {'regex': r'\btest\b', 'paths': ['element12']},  # no such element exists
        {'regex': r'\btest\b', 'paths': ['element13/@attribute']}  # no such attribute exists
    ]

    uninstantiating_cases = [
        {'regex': r'some regex', 'paths': []},  # empty path array
        {'regex': r'some regex', 'paths': ['']},  # paths is an empty string
        {'regex': r'some regex', 'paths': 'path_1'},  # non-array `paths`
        {'regex': r'some regex', 'paths': [3]},  # non-string value in path array
        {'regex': r'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'regex': r'some regex'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
        {'regex': r'[', 'paths': ['path_1']},  # provided string not a valid regex
        {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
        {},  # empty dictionary
        {'regex': r'some regex', 'paths': {'path_1'}},  # dictionary paths
        {'regex': [r'some regex'], 'paths': 'path_1'},  # list regex
        {'regex': r'', 'paths': ['path_1']}  # regex is an empty string
    ]

    invalidating_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']}  # duplicate element
    ]

    nest_case = [{'regex': r'\btest\b', 'paths': ['./element9', './element10/@attribute']}]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'regex_matches'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleRegexMatches."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleRegexMatches."""
        return request.param

    @pytest.fixture(params=nest_case)
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleRegexMatches in nested context."""
        return request.param

    @pytest.fixture(params=nest_case)
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleRegexMatches in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_regexmatches')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_regexmatches')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must match the regular expression' in str(rule_instantiating)


class TestRuleRegexNoMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexNoMatches."""

    all_valid_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']},  # duplicate element
        {'regex': r'\btest\b', 'paths': ['element12']},  # no such element exists
        {'regex': r'\btest\b', 'paths': ['element13/@attribute']}  # no such attribute exists
    ]

    uninstantiating_cases = [
        {'regex': 'some regex', 'paths': []},  # empty path array
        {'regex': r'some regex', 'paths': ['']},  # paths is an empty string
        {'regex': 'some regex', 'paths': 'path_1'},  # non-array `paths`
        {'regex': 'some regex', 'paths': [3]},  # non-string value in path array
        {'regex': 'some regex', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'regex': 'some regex'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `regex`
        {'regex': '[', 'paths': ['path_1']},  # provided string not a valid regex
        {'regex': 3, 'paths': ['path_1']},  # provided regex not a string
        {},  # empty dictionary
        {'regex': 'some regex', 'paths': {'path_1'}},  # dictionary paths
        {'regex': ['some regex'], 'paths': 'path_1'},  # list regex
        {'regex': '', 'paths': ['path_1']}  # regex is an empty string
    ]

    invalidating_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']}  # duplicate element
    ]

    nest_case = [{'regex': r'\btest\b', 'paths': ['./element9', './element10/@attribute']}]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'regex_no_matches'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleRegexNoMatches."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleRegexNoMatches."""
        return request.param

    @pytest.fixture(params=nest_case)
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleRegexNoMatches in nested context."""
        return request.param

    @pytest.fixture(params=nest_case)
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleRegexNoMatches in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_regexnomatches')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_regexnomatches')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must not match the regular expression' in str(rule_instantiating)


class TestRuleStartsWith(RuleSubclassTestBase):
    """A container for tests relating to RuleStartsWith."""

    all_valid_cases = [
        {'start': 'prefix', 'paths': ['element1']},  # single path with valid prefix string
        {'start': 'prefix', 'paths': ['element5/@attribute']},
        {'start': 'prefix', 'paths': ['element2', 'element3']},  # multiple paths with valid prefix string
        {'start': 'prefix', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'start': 'prefix', 'paths': ['element4', 'element4']},  # duplicate paths with valid prefix string
        {'start': 'prefix', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'start': 'prefix', 'paths': ['element11']},  # duplicate element
        {'start': 'prefix', 'paths': ['element12']},  # no such element exists
        {'start': 'prefix', 'paths': ['element13/@attribute']}  # no such attribute exists
    ]

    uninstantiating_cases = [
        {'start': 'prefix-xpath', 'paths': []},  # empty path array
        {'start': 'prefix-xpath', 'paths': 'path_1'},  # non-array `paths`
        {'start': 'prefix-xpath', 'paths': [3]},  # non-string value in path array
        {'start': 'prefix-xpath', 'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {'start': 3, 'paths': ['path_1']},  # provided prefix xpath not a string
        {'start': 'prefix-xpath'},  # missing required attribute - `paths`
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `start`
        {},  # empty dictionary
        {'start': 'prefix-xpath', 'paths': {'path_1'}},  # dictionary paths
        {'start': ['prefix-xpath'], 'paths': ['path_1']},  # list start
        {'start': '', 'paths': ['path_1']},  # start is an empty string
        {'start': 'prefix_path', 'paths': ['']}  # paths is an empty string
    ]

    invalidating_cases = [
        {'start': 'prefix', 'paths': ['element1']},  # single path with valid prefix string
        {'start': 'prefix', 'paths': ['element5/@attribute']},
        {'start': 'prefix', 'paths': ['element2', 'element3']},  # multiple paths with valid prefix string
        {'start': 'prefix', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'start': 'prefix', 'paths': ['element4', 'element4']},  # duplicate paths with valid prefix string
        {'start': 'prefix', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'start': 'prefix', 'paths': ['element11']}  # duplicate element
    ]

    nest_case = [{'start': '//prefix', 'paths': ['element9', 'element10/@attribute']}]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'startswith'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleStartsWith."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleStartsWith."""
        return request.param

    @pytest.fixture(params=nest_case)
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleStartsWith in nested context."""
        return request.param

    @pytest.fixture(params=nest_case)
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleStartsWith in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_startswith')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_startswith')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must start with' in str(rule_instantiating)

    @pytest.mark.parametrize("test_case", [
        {'start': 'duplicateprefix', 'paths': ['element12']},  # `start` matches multiple elements with the same text value
        {'start': 'multiprefix', 'paths': ['element13']}  # `start` matches multiple elements with different text values
    ])
    def test_multiple_matching_start_elements_raise_error(self, valid_single_context, rule_constructor, test_case, invalid_dataset):
        """Check that an error is raised when the specified XPath for `start` returns multiple elements."""
        rule = rule_constructor(valid_single_context, test_case)
        with pytest.raises(ValueError):
            rule.is_valid_for(invalid_dataset)

    def test_missing_start_value_raises_error(self, valid_single_context, rule_constructor, invalid_dataset):
        """Check that if no prefix value is found the rule returns None which is considered equivalent to skipping."""
        missing_value_case = {'start': 'missingprefix', 'paths': ['element14']}
        rule = rule_constructor(valid_single_context, missing_value_case)
        with pytest.raises(ValueError):
            rule.is_valid_for(invalid_dataset)


class TestRuleSum(RuleSubclassTestBase):
    """A container for tests relating to RuleSum.

    Todo:
        **Determine if assumption that double counting of elements should be not permitted when duplicate paths specified, but should when multiple elements exist, is correct.

    """

    all_valid_cases = [
        {'paths': ['element1'], 'sum': 3},  # single path with sum
        {'paths': ['element19/@attribute'], 'sum': 3},
        {'paths': ['element2', 'element3'], 'sum': 3},  # multiple paths with sum
        {'paths': ['element20/@attribute', 'element21/@attribute'], 'sum': 3},
        {'paths': ['element4', 'element4'], 'sum': 3},  # duplicate paths with sum **
        {'paths': ['element22/@attribute', 'element22/@attribute'], 'sum': 3},  # **
        {'paths': ['element5', 'element6'], 'sum': -1000},  # negative sum
        {'paths': ['element23/@attribute', 'element24/@attribute'], 'sum': -1000},
        {'paths': ['element7', 'element8'], 'sum': 101},  # sum greater than standard percentage limit
        {'paths': ['element25/@attribute', 'element26/@attribute'], 'sum': 101},
        {'paths': ['element9', 'element10'], 'sum': 15.5},  # decimal sum
        {'paths': ['element27/@attribute', 'element28/@attribute'], 'sum': 15.5},
        {'paths': ['element11', 'element12'], 'sum': 0},  # zero sum
        {'paths': ['element29/@attribute', 'element30/@attribute'], 'sum': 0},
        {'paths': ['element13', 'element14'], 'sum': float(10**100)},  # big sum
        {'paths': ['element31/@attribute', 'element32/@attribute'], 'sum': float(10**100)},
        {'paths': ['element15', 'element16'], 'sum': float(-10**100)},  # tiny sum
        {'paths': ['element33/@attribute', 'element34/@attribute'], 'sum': float(-10**100)},
        {'paths': ['element17', 'element18'], 'sum': 2.99792458e6},  # exponential sum
        {'paths': ['element35/@attribute', 'element36/@attribute'], 'sum': 2.99792458e6},
        {'paths': ['element37'], 'sum': 50},  # duplicate elements in data **
        {'paths': ['element42', 'element43'], 'sum': 0.3},  # sum to value that cannot be represented using standard binary representation
        {'paths': ['element44/@attribute', 'element45/@attribute'], 'sum': 0.3},
        {'paths': ['element46'], 'sum': 50}  # whitespace around numeric value
    ]

    uninstantiating_cases = [
        {'paths': [], 'sum': 3},  # empty path array
        {'paths': 'path_1', 'sum': 3},  # non-array `paths`
        {'paths': [3], 'sum': 3},  # non-string value in path array
        {'paths': ['path_1', 3], 'sum': 3},  # mixed string and non-string value in path array
        {'paths': ['path_1', 'path_2']},  # missing required attribute - `sum`
        {'sum': 100},  # missing required attribute - `paths`
        {},  # empty dictionary
        {'paths': ['path_1'], 'sum': '3'},  # sum is a string representation of a number
        {'sum': 100, 'paths': {'path_1'}},  # dictionary paths
        {'sum': [100], 'paths': 'path_1'},  # list sum
        {'paths': [''], 'sum': 100},  # empty paths string
        {'paths': ['path_1'], 'sum': ''}  # sum is empty string
    ]

    invalidating_cases = [
        {'paths': ['element1'], 'sum': 3},  # single path with sum
        {'paths': ['element19/@attribute'], 'sum': 3},
        {'paths': ['element2', 'element3'], 'sum': 3},  # multiple paths with sum
        {'paths': ['element20/@attribute', 'element21/@attribute'], 'sum': 3},
        {'paths': ['element4', 'element4'], 'sum': 3},  # duplicate paths with sum **
        {'paths': ['element22/@attribute', 'element22/@attribute'], 'sum': 3},  # **
        {'paths': ['element5', 'element6'], 'sum': -1000},  # negative sum
        {'paths': ['element23/@attribute', 'element24/@attribute'], 'sum': -1000},
        {'paths': ['element7', 'element8'], 'sum': 101},  # sum greater than standard percentage limit
        {'paths': ['element25/@attribute', 'element26/@attribute'], 'sum': 101},
        {'paths': ['element9', 'element10'], 'sum': 15.5},  # decimal sum
        {'paths': ['element27/@attribute', 'element28/@attribute'], 'sum': 15.5},
        {'paths': ['element11', 'element12'], 'sum': 0},  # zero sum
        {'paths': ['element29/@attribute', 'element30/@attribute'], 'sum': 0},
        {'paths': ['element13', 'element14'], 'sum': float(10**100)},  # big sum
        {'paths': ['element31/@attribute', 'element32/@attribute'], 'sum': float(10**100)},
        {'paths': ['element15', 'element16'], 'sum': float(-10**100)},  # tiny sum
        {'paths': ['element33/@attribute', 'element34/@attribute'], 'sum': float(-10**100)},
        {'paths': ['element17', 'element18'], 'sum': 2.99792458e6},  # exponential sum
        {'paths': ['element35/@attribute', 'element36/@attribute'], 'sum': 2.99792458e6},
        {'paths': ['element37'], 'sum': 50}  # duplicate elements in data **
    ]

    nest_cases = [
        {'paths': ['//element38', '//element39'], 'sum': 3},
        {'paths': ['//element40/@attribute', '//element41/@attribute'], 'sum': 3}
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'sum'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleSum."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleSum."""
        return request.param

    @pytest.fixture(params=nest_cases)
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleSum in nested context."""
        return request.param

    @pytest.fixture(params=nest_cases)
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleSum in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_sum')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_sum')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'sum of values' in str(rule_instantiating)

    @pytest.mark.parametrize("test_case", [
        {'paths': ['element42'], 'sum': 50}  # non-numeric value
    ])
    def test_non_numeric_value_raise_error(self, valid_single_context, rule_constructor, test_case, invalid_dataset):
        """Check that an error is raised when the specified XPath for `start` returns multiple elements."""
        rule = rule_constructor(valid_single_context, test_case)
        with pytest.raises(ValueError):
            rule.is_valid_for(invalid_dataset)

    def test_no_values_to_sum_skips(self, valid_single_context, rule_constructor, valid_dataset):
        """Check that the Rule is skipped if no values are found to compare to the value of `sum`."""
        no_values_case = {'paths': ['this_element_does_not_exist', 'neither_does_this_one'], 'sum': 100}
        rule = rule_constructor(valid_single_context, no_values_case)
        assert rule.is_valid_for(valid_dataset) is None


class TestRuleUnique(RuleSubclassTestBase):
    """A container for tests relating to RuleUnique."""

    all_valid_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element5/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element6/@attribute', 'element7/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element8/@attribute', 'element8/@attribute']},
        {'paths': ['element13']},  # duplicate elements exist for path
        {'paths': ['element14']},  # no such element exists
        {'paths': ['element15/@attribute']}  # no such attribute exists
    ]

    uninstantiating_cases = [
        {'paths': []},  # empty path array
        {'paths': 'path_1'},  # non-array `paths`
        {'paths': [3]},  # non-string value in path array
        {'paths': ['path_1', 3]},  # mixed string and non-string value in path array
        {},  # empty dictionary
        {'paths': {'path_1'}}
    ]

    invalidating_cases = [
        {'paths': ['element1', 'element2']},  # multiple paths
        {'paths': ['element3/@attribute', 'element4/@attribute']},
        {'paths': ['element9']}  # duplicate elements exist for path
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'unique'

    @pytest.fixture(params=[all_valid_cases[0]])
    def single_instantiating_case(self, request):
        """Single permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def instantiating_case(self, request):
        """Permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=uninstantiating_cases)
    def uninstantiating_case(self, request):
        """Non-permitted case for instatiating this Rule."""
        return request.param

    @pytest.fixture(params=all_valid_cases)
    def validating_case(self, request):
        """Permitted cases for validating an XML dataset against RuleUnique."""
        return request.param

    @pytest.fixture(params=invalidating_cases)
    def invalidating_case(self, request):
        """Non-permitted cases for validating an XML dataset against RuleUnique."""
        return request.param

    @pytest.fixture(params=[
        {'paths': ['element9', 'element10']},
        {'paths': ['element11/@attribute', 'element12/@attribute']}
    ])
    def valid_nest_case(self, request):
        """Permitted case for validating an XML dataset against RuleUnique in nested context."""
        return request.param

    @pytest.fixture(params=[
        {'paths': ['element5', 'element6']},
        {'paths': ['element7/@attribute', 'element8/@attribute']}
    ])
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleUnique in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/invalid_unique')

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.tests.resources.load_as_dataset('ruleset/valid_unique')

    def test_rule_string_output_specific(self, rule_instantiating):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must be unique' in str(rule_instantiating)
