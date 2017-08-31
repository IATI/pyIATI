"""A module containing tests for the library representation of Rulesets."""
from copy import deepcopy
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
        """Check that a Ruleset is created when given a JSON Ruleset in string format."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": []}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert ruleset.rules == set()

    @pytest.mark.parametrize("not_a_ruleset", iati.core.tests.utilities.find_parameter_by_type(['str', 'bytearray'], False))
    def test_ruleset_init_ruleset_str_not_str(self, not_a_ruleset):
        """Check that a Ruleset cannot be created when given at least one Rule in a non-string format."""
        with pytest.raises(ValueError):
            iati.core.Ruleset(not_a_ruleset)

    @pytest.mark.parametrize("byte_array", iati.core.tests.utilities.find_parameter_by_type(['bytearray']))
    def test_ruleset_init_ruleset_str_bytearray(self, byte_array):
        """Check that a Ruleset cannot be created when given at least one Rule in a bytearray format."""
        with pytest.raises(ValueError):
            iati.core.Ruleset(byte_array)

    def test_ruleset_init_ruleset_str_invalid(self):
        """Check that a Ruleset cannot be created when given a string that is not a Ruleset."""
        not_a_ruleset_str = 'This is not a ruleset: It is a cat. Meow, meow.'

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
        assert isinstance(list(ruleset.rules)[0], iati.core.RuleAtLeastOne)

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
            assert isinstance(rule, iati.core.RuleAtLeastOne)

    def test_ruleset_init_ruleset_multiple_cases(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with two Rules of different types, each under the same context."""
        ruleset_str = '{"CONTEXT": {"atleast_one": {"cases": [{"paths": ["test_path_1"]}]}, "no_more_than_one": {"cases": [{"paths": ["test_path_2"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 2
        for rule in ruleset.rules:
            assert isinstance(rule, iati.core.Rule)
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.RuleAtLeastOne)]) == 1
        assert len([rule for rule in ruleset.rules if isinstance(rule, iati.core.RuleNoMoreThanOne)]) == 1

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
            assert isinstance(rule, iati.core.RuleAtLeastOne)


class TestRule(object):
    """A container for tests relating to Rules."""

    def test_rule_class_cannot_be_instantiated_directly_without_name(self):
        """Check that Rule itself cannot be directly instantiated."""
        context = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(AttributeError):
            iati.core.Rule(context, case)

    def test_rule_class_cannot_be_instantiated_directly_with_name(self):
        """Check that Rule itself cannot be directly instantiated with a Rule name."""
        name = 'atleast_one'
        context = 'an xpath'
        case = {'paths': ['path_1', 'path_2']}

        with pytest.raises(TypeError):
            iati.core.Rule(name, context, case)


class TestRuleSubclasses(object):
    """A container for tests relating to all Rule subclasses."""

    @pytest.fixture(params=[
        iati.core.rulesets.constructor_for_rule_type(rule_type) for rule_type in iati.core.rulesets._VALID_RULE_TYPES
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

    @pytest.mark.parametrize("case", iati.core.tests.utilities.find_parameter_by_type(['mapping'], False))
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


class RuleSubclassTestBase(object):
    """A base class for Rule subclass tests."""

    @pytest.fixture
    def valid_single_context(self):
        """Return valid context with a single match."""
        return '//root_element'

    @pytest.fixture
    def valid_multiple_context(self):
        """Return a valid context with multiple matches."""
        return '//nest'

    @pytest.fixture(params=[
        'count(condition)>0',
        'condition'
    ])
    def valid_condition_case(self, validating_case, request):
        """Return a case with optional condition attribute."""
        condition_validating_case = deepcopy(validating_case)
        condition_validating_case['condition'] = request.param
        return condition_validating_case

    @pytest.fixture(params=[
        'count(condition)>0',
        'condition'
    ])
    def invalid_condition_case(self, invalidating_case, request):
        """Return a case with optional condition attribute."""
        condition_invalidating_case = deepcopy(invalidating_case)
        condition_invalidating_case['condition'] = request.param
        return condition_invalidating_case

    @pytest.fixture
    def rule_basic_init(self, rule_constructor, instantiating_case, valid_single_context):
        """Rule subclass."""
        return rule_constructor(valid_single_context, instantiating_case)

    @pytest.fixture
    def rule_is_valid_for(self, rule_constructor, validating_case, valid_single_context):
        """Rule subclass for validation."""
        return rule_constructor(valid_single_context, validating_case)

    @pytest.fixture
    def rule_is_invalid_for(self, rule_constructor, invalidating_case, valid_single_context):
        """Rule with specific cases for checking the `is_valid_for` function."""
        return rule_constructor(valid_single_context, invalidating_case)

    @pytest.fixture
    def rule_constructor(self, rule_type):
        """Return current Rule type.

        Note:
            Differs from fixture of same name in TestRuleSubclass as specifies rule_type via specific TestRuleSubclass fixture.

        """
        return iati.core.rulesets.constructor_for_rule_type(rule_type)

    @pytest.fixture
    def valid_condition_rule(self, rule_constructor, valid_single_context, valid_condition_case):
        """Return a Rule with a `condition` case."""
        return rule_constructor(valid_single_context, valid_condition_case)

    @pytest.fixture
    def invalid_condition_rule(self, rule_constructor, valid_single_context, invalid_condition_case):
        """Return a Rule with a `condition` case."""
        return rule_constructor(valid_single_context, invalid_condition_case)

    def test_rule_init_valid_parameter_types(self, rule_basic_init):
        """Check that Rule subclasses can be instantiated with valid parameter types."""
        assert isinstance(rule_basic_init, iati.core.Rule)

    def test_rule_init_raises_error_on_empty_context(self, rule_constructor, instantiating_case):
        """Check that a Rule cannot be instantiated when the `context` is an empty string."""
        invalid_context = ''
        with pytest.raises(ValueError):
            rule_constructor(invalid_context, instantiating_case)

    def test_rule_attributes_from_case(self, rule_basic_init):
        """Check that a Rule subclass has case attributes set."""
        required_attributes = rule_basic_init._case_attributes(rule_basic_init._ruleset_schema_section())
        for attrib in required_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(rule_basic_init, attrib)

    def test_optional_rule_attributes_from_case(self, rule_constructor, valid_single_context, valid_condition_case):
        """Check that a Rule subclass has case attributes set."""
        rule = rule_constructor(valid_single_context, valid_condition_case)
        optional_attributes = rule._case_attributes(rule._ruleset_schema_section(), False)
        for attrib in optional_attributes:
            # Ensure that the attribute exists - if not, an AttributeError will be raised
            getattr(rule, attrib)

    def test_rule_name(self, rule_basic_init, rule_type):
        """Check that a Rule subclass has the expected name."""
        assert rule_basic_init.name == rule_type

    def test_rule_string_output_general(self, rule_basic_init):
        """Check that the string format of the Rule has been customised and variables formatted."""
        assert 'iati.core.rulesets' not in str(rule_basic_init)
        assert ' object at ' not in str(rule_basic_init)
        assert 'self' not in str(rule_basic_init)
        assert '{0}' not in str(rule_basic_init)

    @pytest.mark.parametrize("context", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_rule_init_invalid_context(self, rule_constructor, context, instantiating_case):
        """Check that a Rule subclass cannot be created when context is not a string."""
        with pytest.raises(TypeError):
            rule_constructor(context, instantiating_case)

    def test_rule_invalid_case(self, rule_constructor, uninstantiating_case):
        """Check that a Rule cannot be instantiated when the case is not permitted."""
        context = 'an xpath'
        with pytest.raises(ValueError):
            rule_constructor(context, uninstantiating_case)

    def test_is_valid_for(self, valid_dataset, rule_is_valid_for):
        """Check that a given Rule returns the expected result when given Dataset."""
        assert rule_is_valid_for.is_valid_for(valid_dataset)

    def test_is_invalid_for(self, invalid_dataset, rule_is_invalid_for):
        """Check that a given Rule returns the expected result when given a Dataset."""
        assert not rule_is_invalid_for.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_data", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_is_valid_for_raises_error_on_non_permitted_argument(self, rule_basic_init, junk_data):
        """Check that a given Rule returns expected error when passed an argument that is not a Dataset."""
        with pytest.raises(AttributeError):
            rule_basic_init.is_valid_for(junk_data)

    def test_is_valid_for_raises_error_when_passed_an_etree(self, rule_basic_init):
        """Check that an error is raised if an etree is given as an argument instead of a Dataset.

        Todo:
            Use more generic Dataset.

        """
        with pytest.raises(AttributeError):
            rule_basic_init.is_valid_for(iati.core.resources.load_as_tree(iati.core.resources.get_test_data_path('valid_atleastone')))

    def test_multiple_valid_context_matches_is_valid_for(self, valid_multiple_context, valid_nest_case, rule_constructor, valid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(valid_multiple_context, valid_nest_case)
        assert rule.is_valid_for(valid_dataset)

    def test_multiple_valid_context_matches_is_invalid_for(self, valid_multiple_context, invalid_nest_case, rule_constructor, invalid_dataset):
        """Check Rule returns expected result when checking multiple contexts."""
        rule = rule_constructor(valid_multiple_context, invalid_nest_case)
        assert not rule.is_valid_for(invalid_dataset)

    def test_condition_case_is_True(self, valid_condition_rule, valid_dataset):
        """Check that if a condition is `True`, the rule returns None."""
        assert valid_condition_rule.is_valid_for(valid_dataset) is None

    def test_condition_case_is_False(self, invalid_condition_rule, invalid_dataset):
        """Check that if a condition is `False`, the rule validates normally.

        Note:
            Using an invalid dataset so expecting Rules to evaluate to `False`.

        """
        assert not invalid_condition_rule.is_valid_for(invalid_dataset)

    @pytest.mark.parametrize("junk_condition", [''] + iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_uninstantiating_condition_case(self, rule_constructor, valid_single_context, validating_case, junk_condition):
        """Check that a non-permitted condition case will not instantiate."""
        junk_condition_case = deepcopy(validating_case)
        junk_condition_case['condition'] = junk_condition
        with pytest.raises(Exception):
            rule_constructor(valid_single_context, junk_condition_case)


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
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_VALID

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_ATLEASTONE_RULE_INVALID

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must be present' in str(rule_basic_init)


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
        {'less': 'element37', 'more': 'element38'}  # multiple identical elements
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
        {'less': 'element3', 'more': 'element4'},  # dates have identical values
        {'less': 'element16/@attribute', 'more': 'element17/@attribute'},
        {'less': 'NOW', 'more': 'element5'},  # `more` is chronologically before NOW
        {'less': 'NOW', 'more': 'element18/@attribute'},
        {'less': 'element6', 'more': 'NOW'},  # `less` is chronologically after NOW
        {'less': 'element19/@attribute', 'more': 'NOW'},
        {'less': '//element7', 'more': '//element8'},  # nested dates not in chronological order
        {'less': '//element20/@attribute', 'more': '//element21/@attribute'},
        {'less': 'element9', 'more': 'element9'},  # `less` and `more` reference the same date
        {'less': 'element22/@attribute', 'more': 'element22/@attribute'},
        {'less': 'element10', 'more': 'element11'},  # multiple identical `less` dates that are chronologically after `more`
        {'less': 'element23/@attribute', 'more': 'element24/@attribute'},
        {'less': 'element12', 'more': 'element13'},  # multiple identical `more` dates that are chronologically before `less`
        {'less': 'element25/@attribute', 'more': 'element26/@attribute'},
        {'less': 'element27', 'more': 'element28'}  # multiple identical elements in incorrect order
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'date_order'

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
        return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_VALID

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
        {'less': 'element41', 'more': 'element42'}  # multiple identical elements but non-duplicated values
    ])
    def test_incorrect_date_format_raises_error(self, valid_single_context, case, rule_constructor):
        """Check that a dataset with dates in an incorrect format raise expected error."""
        rule = rule_constructor(valid_single_context, case)
        with pytest.raises(ValueError):
            rule.is_valid_for(iati.core.tests.utilities.DATASET_FOR_DATEORDER_RULE_INVALID_DATE_FORMAT)

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

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_basic_init) for needle in ['must be chronologically', 'in the future', 'in the past'])


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
        {'paths': ['./element9/@attribute', './element10/@attribute']}
    ])
    def invalid_nest_case(self, request):
        """Non-permitted case for validating an XML dataset against RuleDependent in nested context."""
        return request.param

    @pytest.fixture
    def invalid_dataset(self):
        """Invalid dataset for instatiating this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_DEPENDENT_RULE_VALID

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_basic_init) for needle in ['must all exist', 'always True'])


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
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element8/@attribute', 'element9/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element10/@attribute', 'element10/@attribute']},
        {'paths': ['element5', 'element6']},  # one path valid, another invalid
        {'paths': ['element11/@attribute', 'element12/@attribute']}
    ]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'no_more_than_one'

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
        return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_NOMORETHANONE_RULE_VALID

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert any(needle in str(rule_basic_init) for needle in ['zero or one', 'no more than one'])


class TestRuleRegexMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexMatches."""

    all_valid_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']}  # duplicate element
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
        return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXMATCHES_RULE_VALID

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must match the regular expression' in str(rule_basic_init)


class TestRuleRegexNoMatches(RuleSubclassTestBase):
    """A container for tests relating to RuleRegexNoMatches."""

    all_valid_cases = [
        {'regex': r'\btest\b', 'paths': ['element1']},  # single path with regex
        {'regex': r'\btest\b', 'paths': ['element5/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element2', 'element3']},  # multiple paths with regex
        {'regex': r'\btest\b', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element4', 'element4']},  # duplicate paths with regex
        {'regex': r'\btest\b', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'regex': r'\btest\b', 'paths': ['element11']}  # duplicate element
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
        return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_REGEXNOMATCHES_RULE_VALID

    def test_rule_string_output_specific(self, rule_basic_init):
        """Check that the string format of the Rule contains some relevant information."""
        assert 'must not match the regular expression' in str(rule_basic_init)

class TestRuleStartsWith(RuleSubclassTestBase):
    """A container for tests relating to RuleStartsWith."""

    all_valid_cases = [
        {'start': 'prefix', 'paths': ['element1']},  # single path with valid prefix string
        {'start': 'prefix', 'paths': ['element5/@attribute']},
        {'start': 'prefix', 'paths': ['element2', 'element3']},  # multiple paths with valid prefix string
        {'start': 'prefix', 'paths': ['element6/@attribute', 'element7/@attribute']},
        {'start': 'prefix', 'paths': ['element4', 'element4']},  # duplicate paths with valid prefix string
        {'start': 'prefix', 'paths': ['element8/@attribute', 'element8/@attribute']},
        {'start': 'prefix', 'paths': ['element11']}  # duplicate element
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

    nest_case = [{'start': 'prefix', 'paths': ['element9', 'element10/@attribute']}]

    @pytest.fixture
    def rule_type(self):
        """Type of Rule."""
        return 'startswith'

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
        return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_STARTSWITH_RULE_VALID


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
        {'paths': ['element37'], 'sum': 50}  # duplicate elements in data **
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
        return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_SUM_RULE_VALID


class TestRuleUnique(RuleSubclassTestBase):
    """A container for tests relating to RuleUnique."""

    all_valid_cases = [
        {'paths': ['element1']},  # single path
        {'paths': ['element5/@attribute']},
        {'paths': ['element2', 'element3']},  # multiple paths
        {'paths': ['element6/@attribute', 'element7/@attribute']},
        {'paths': ['element4', 'element4']},  # duplicate paths
        {'paths': ['element8/@attribute', 'element8/@attribute']},
        {'paths': ['element13']}  # duplicate elements exist for path
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
        return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_INVALID

    @pytest.fixture
    def valid_dataset(self):
        """Return valid dataset for this Rule."""
        return iati.core.tests.utilities.DATASET_FOR_UNIQUE_RULE_VALID
