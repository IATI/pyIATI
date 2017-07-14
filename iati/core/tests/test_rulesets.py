"""A module containing tests for the library representation of Rulesets."""
import pytest
import iati.core.default
import iati.core.rulesets
import iati.core.resources


class TestRuleset(object):
    """A container for tests relating to Rulesets."""

    def test_ruleset_init_no_parameters(self):
        """Check that a Ruleset cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            iati.core.Ruleset()

    def test_ruleset_init_ruleset_str_valid(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format."""
        ruleset_str = '{"CONTEXT": {"RULE_NAME": {"cases": []}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 0

    @pytest.mark.parametrize("not_a_ruleset", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_ruleset_init_ruleset_str_not_str(self, not_a_ruleset):
        """Check that a Ruleset cannot be created when given at least one Rule in a non-string format."""
        with pytest.raises(TypeError):
            iati.core.Ruleset(not_a_ruleset)

    def test_ruleset_init_ruleset_str_invalid(self):
        """Check that a Ruleset cannot be created when given a string that is not a Ruleset."""
        not_a_ruleset_str = 'this is not a ruleset: it is a cat'

        with pytest.raises(ValueError):
            iati.core.Ruleset(not_a_ruleset_str)

    def test_ruleset_init_ruleset_1_rule(self):
        """Check that a Ruleset can be created when given a JSON Ruleset in string format with at least one Rule."""
        ruleset_str = '{"CONTEXT": {"RULE_NAME": {"cases": [{"paths": ["test_path"]}]}}}'

        ruleset = iati.core.Ruleset(ruleset_str)

        assert isinstance(ruleset, iati.core.Ruleset)
        assert isinstance(ruleset.rules, set)
        assert len(ruleset.rules) == 1
        assert isinstance(list(ruleset.rules)[0], iati.core.Rule)

    def test_ruleset_instantiation(self):
        """Ruleset object correctly instantiates."""
        # ruleset_str = iati.core.default.ruleset()
        # format_ruleset_str = ruleset_str.decode('utf-8')
        # ruleset = iati.core.rulesets.Ruleset(format_ruleset_str)
        # rule_item = list(ruleset.rules)[0]
        # assert isinstance(ruleset, iati.core.rulesets.Ruleset)
        # assert len(ruleset.rules) > 1
        # assert isinstance(rule_item, iati.core.rulesets.Rule)

    def test_ruleset_implementation(self):
        """Ruleset rules execute their implemenation correctly as a set."""


class TestRule(object):
    """A container for tests relating to Rules."""

    def test_rule_init_no_parameters(self):
        """Check that a Rule cannot be created when no parameters are given."""
        with pytest.raises(TypeError):
            iati.core.Rule()

    def test_rule_init_valid_parameter_types(self):
        """Check that a Rule can be created when given correct parameters."""
        rule_type = 'the name of the Rule'
        xpath_base = 'an xpath'
        case = dict()

        rule = iati.core.Rule(rule_type, xpath_base, case)

        assert isinstance(rule, iati.core.Rule)
        assert rule.rule_type == rule_type
        assert rule.xpath_base == xpath_base
        assert rule.case == case

    @pytest.mark.parametrize("rule_type", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_rule_init_invalid_rule_type(self, rule_type):
        """Check that a Rule cannot be created when rule_type is not a string."""
        xpath_base = 'an xpath'
        case = dict()

        with pytest.raises(TypeError):
            iati.core.Rule(rule_type, xpath_base, case)

    @pytest.mark.parametrize("xpath_base", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_rule_init_invalid_xpath_base(self, xpath_base):
        """Check that a Rule cannot be created when xpath_base is not a string."""
        rule_type = 'the name of the Rule'
        case = dict()

        with pytest.raises(TypeError):
            iati.core.Rule(rule_type, xpath_base, case)

    @pytest.mark.parametrize("case", iati.core.tests.utilities.find_parameter_by_type(['mapping'], False))
    def test_rule_init_invalid_case_type(self, case):
        """Check that a Rule cannot be created when case is not a dictionary."""
        rule_type = 'the name of the Rule'
        xpath_base = 'an xpath'

        with pytest.raises(TypeError):
            iati.core.Rule(rule_type, xpath_base, case)

    @pytest.mark.parametrize("rule_type", iati.core.rulesets._VALID_RULE_TYPES)
    def test_rule_init_rule_valid_type(self, rule_type):
        """Check that valid rule_type values may be used in the initialisation of a Rule."""
        xpath_base = 'an xpath'
        case = dict()

        rule = iati.core.Rule(rule_type, xpath_base, case)

        assert isinstance(rule, iati.core.Rule)

    @pytest.mark.parametrize("rule_type", iati.core.tests.utilities.find_parameter_by_type(['str']))
    def test_rule_init_invalid_rule_type_raises_error(self, rule_type):
        """Check that invalid rule_type values cause an error."""
        # xpath_base = 'an xpath'
        # case = dict()
        #
        # with pytest.raises(ValueError) as excinfo:
        #     iati.core.Rule(rule_type, xpath_base, case)

        pass

    # def test_rule_instantiation(self):
    #     """Rule object correctly instantiates."""
    #     name = 'atleast_one'
    #     xpath_base = '//iati-activity'
    #     case = {"paths": ["activity-date[@type='1' or @type='2']"]}
    #     rule = iati.core.rulesets.RuleAtLeastOne(name, xpath_base, case)
    #     assert isinstance(rule, iati.core.rulesets.Rule)
    #     assert rule.name == 'atleast_one'
    #     assert isinstance(rule.case, dict)

    # def test_RuleNoMoreThanOne_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleAtLeastOne_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleDependent_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleSum_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleDateOrder_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleRegexMatches_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleRegexNoMatches_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleStartsWith_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass

    # def test_RuleUnique_implementation(self):
    #     """Rule executes its implementation correctly."""
    #     pass
