"""A module containg a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Warning:
    The contents of this module have not been implemented. Their structure may change when they are implemented.

Todo:
    Implement Rulesets (and Rules). Likely worth completing the Codelist implementation first since the two will be similar.

"""

import json
import sys
import six
import iati.core.utilities


_VALID_RULE_TYPES = ["no_more_than_one", "atleast_one", "dependent", "sum", "date_order", "regex_matches", "regex_no_matches", "startswith", "unique"]


class Ruleset(object):
    """Representation of a Ruleset as defined within the IATI SSOT.

    Warning:
        Rulesets have not yet been implemented. They will likely have a similar API to Codelists, although this is yet to be determined.

    """

    def __init__(self, ruleset_str):
        """Initialise a Ruleset.

        Args:
            ruleset_str (str): A string that represents a Ruleset.

        Raises:
            KeyError: When a rule_type within the ruleset_str is not permitted.
            TypeError: When a ruleset_str is not a string.
            ValueError: When ruleset_str is not a JSON string.
            ValueError: When keys in the same scope of the ruleset_str are duplicated.

        """
        if not isinstance(ruleset_str, str):
            raise TypeError

        # if parsing fails, raises a ValueError
        ruleset = json.loads(ruleset_str, object_pairs_hook=iati.core.utilities.dict_raise_on_duplicates)
        self.rules = set()

        for xpath_base, rule in ruleset.items():
            for rule_type, cases in rule.items():
                for case in cases['cases']:
                    constructor = self._locate_constructor_for_rule_type(rule_type)
                    new_rule = constructor(xpath_base, case)
                    self.rules.add(new_rule)

    def _locate_constructor_for_rule_type(self, rule_type):
        """Locate the constructor for specific rule types.

        Args:
            rule_type (str): The name of the type of Rule to identify the class for.

        Returns:
            Rule implementation: A constructor for a class that inherits from Rule.

        Raises:
            KeyError: When a non-permitted `rule_type` is provided.

        """
        possible_rule_types = {
            'atleast_one': RuleAtLeastOne,
            # 'date_order': RuleDateOrder,
            # 'dependent': RuleDependent,
            'no_more_than_one': RuleNoMoreThanOne #,
            # 'regex_matches': RuleRegexMatches,
            # 'regex_no_matches': RuleRegexNoMatches,
            # 'startswith': RuleStartsWith,
            # 'sum': RuleSum,
            # 'unique': RuleUnique
        }

        return possible_rule_types[rule_type]



class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually do something.

    """

    def __init__(self, xpath_base, case):
        """Initialise a Rule.

        Args:
            xpath_base (str): The base of the XPath that the Rule will act upon.
            case (dict): Specific configuration for this instance of the Rule.

        Raises:
            TypeError: When a parameter is of an incorrect type.
            ValueError: When a rule_type is not one of the permitted Rule types.

        """
        if not isinstance(xpath_base, six.string_types) or not isinstance(case, dict):
            raise TypeError

        self.xpath_base = xpath_base


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """
    def __init__(self, xpath_base, case):
        super(Rule, self).__init__()
        # super.__init__(xpath_base, case)
        self.name = "no_more_than_one"
        # try:
        #     self.paths = case['path']
        # except KeyError:
        #     raise KeyError("y u no give me a paths D:")


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """

    def implementation(self, dataset):
        """Check activity has at least one instance of a given case."""
        pass
