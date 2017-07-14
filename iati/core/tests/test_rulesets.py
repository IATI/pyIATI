"""A module containing tests for the library representation of Rulesets."""
import iati.core.default
import iati.core.rulesets
import iati.core.resources


class TestRuleset(object):
    """A container for tests relating to Rulesets."""

    def test_ruleset_instantiation(self):
        """Ruleset object correctly instantiates."""
        ruleset_str = iati.core.default.ruleset()
        format_ruleset_str = ruleset_str.decode('utf-8')
        ruleset = iati.core.rulesets.Ruleset(format_ruleset_str)
        rule_item = list(ruleset.rules)[0]
        assert isinstance(ruleset, iati.core.rulesets.Ruleset)
        assert len(ruleset.rules) > 1
        assert isinstance(rule_item, iati.core.rulesets.Rule)

    def test_ruleset_implementation(self):
        """Ruleset rules execute their implemenation correctly as a set."""


class TestRules(object):
    """A container for tests relating to Rules."""

    def test_rule_instantiation(self):
        """Rule object correctly instantiates."""
        name = 'atleast_one'
        xpath_base = '//iati-activity'
        case = {"paths": ["activity-date[@type='1' or @type='2']"]}
        rule = iati.core.rulesets.RuleAtLeastOne(name, xpath_base, case)
        assert isinstance(rule, iati.core.rulesets.Rule)
        assert rule.name == 'atleast_one'
        assert isinstance(rule.case, dict)

    def test_RuleNoMoreThanOne_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleAtLeastOne_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleDependent_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleSum_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleDateOrder_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleRegexMatches_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleRegexNoMatches_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleStartsWith_implementation(self):
        """Rule executes its implementation correctly."""
        pass

    def test_RuleUnique_implementation(self):
        """Rule executes its implementation correctly."""
        pass
