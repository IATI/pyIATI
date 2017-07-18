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
            TypeError: When a ruleset_str is not a string.

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
                    new_rule = constructor(rule_type, xpath_base, case)
                    self.rules.add(new_rule)

    def _locate_constructor_for_rule_type(self, rule_type):
        """Locate the constructor for specific rule types.

        Args:
            rule_type (str): The name of the type of Rule to identify the class for.

        Returns:
            Rule implementation: A constructor for a class that inherits from Rule.

        Raises:
            ValueError: When a non-permitted `rule_type` is provided.

        Todo:
            Implement ValueError.

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

    def __init__(self, rule_type, xpath_base, case):
        """Initialise a Rule.

        Args:
            rule_type (str): The type of the Rule.
            xpath_base (str): The base of the XPath that the Rule will act upon.
            case (dict): Specific configuration for this instance of the Rule.

        Raises:
            TypeError: When a parameter is of an incorrect type.
            ValueError: When a rule_type is not one of the permitted Rule types.

        """
        if isinstance(rule_type, bytes):
            rule_type = str(rule_type)

        if not isinstance(rule_type, six.string_types) or not isinstance(xpath_base, six.string_types) or not isinstance(case, dict):
            raise TypeError

        if rule_type in _VALID_RULE_TYPES:
            self.rule_type = rule_type
        else:
            raise ValueError

        self.xpath_base = xpath_base
        self.case = case


# class Ruleset(object):
#     """Representation of a Ruleset as defined within the IATI SSOT.

#     Warning:
#         Rulesets have not yet been implemented. They will likely have a similar API to Codelists, although this is yet to be determined.

#     """

#     def __init__(self, ruleset_str):
#         """Initialise a Ruleset."""
#         self._json = json.loads(ruleset_str)
#         self.rules = set()
#         self.set_rules()

#     def set_rules(self):
#         """Add Rules to rules set."""
#         for xpath_base, rule in self._json.items():
#             for rule_name, cases in rule.items():
#                 for case in cases['cases']:
#                     implement_rule = self.match_rule(rule_name, xpath_base, case)
#                     self.rules.add(implement_rule)

#     def match_rule(self, rule_name, xpath_base, case):
#         """Match rule_name to specific Rule implementation."""
#         possible_rule_names = {'no_more_than_one': RuleNoMoreThanOne,
#                                'atleast_one': RuleAtLeastOne,
#                                'dependent': RuleDependent,
#                                'sum': RuleSum,
#                                'date_order': RuleDateOrder,
#                                'regex_matches': RuleRegexMatches,
#                                'regex_no_matches': RuleRegexNoMatches,
#                                'startswith': RuleStartsWith,
#                                'unique': RuleUnique}

#         return possible_rule_names[rule_name](rule_name, xpath_base, case)


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """

    pass


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """

    def implementation(self, dataset):
        """Check activity has at least one instance of a given case."""
        pass
