"""A module containing tests for the library representation of Rulesets."""
import iati.core.default
import iati.core.rulesets


class TestRuleset(object):
    """A container for tests relating to Rulesets."""

    def test_ruleset_instantiation(self):
        """Ruleset object correctly instantiates."""
        ruleset_str = iati.core.default.ruleset()
        format_ruleset_str = ruleset_str.decode('utf-8')
        ruleset = iati.core.rulesets.Ruleset(format_ruleset_str)
        rule_item = list(ruleset.rules)[0]
        assert isinstance(ruleset, iati.core.rulesets.Ruleset)
        assert len(ruleset.rules) >= 1
        assert isinstance(rule_item, iati.core.rulesets.Rule)
