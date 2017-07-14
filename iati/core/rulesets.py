"""A module containg a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Warning:
    The contents of this module have not been implemented. Their structure may change when they are implemented.

Todo:
    Implement Rulesets (and Rules). Likely worth completing the Codelist implementation first since the two will be similar.

"""

import json


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

        """
        if not isinstance(ruleset_str, str):
            raise TypeError

        ruleset = json.loads(ruleset_str)

        self.rules = set()

        for xpath_base, rule in ruleset.items():
            for rule_type, cases in rule.items():
                if len(cases['cases']) > 0:
                    self.rules.add(Rule(rule_type, xpath_base, cases))


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually do something.

    """

    def __init__(self, rule_type, xpath_base, case):
        """Initialise a Rule."""
        if isinstance(rule_type, bytes):
            rule_type = rule_type.decode('cp437')

        if not isinstance(rule_type, str) or not isinstance(xpath_base, str) or not isinstance(case, dict):
            raise TypeError

        if rule_type in _VALID_RULE_TYPES:
            self.rule_type = rule_type
        else:
            raise ValueError

        self.xpath_base = xpath_base
        self.case = case

# import json


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


# class Rule(object):
#     """Representation of a Rule contained within a Ruleset.

#     Acts as a base class for specific types of Rule that actually do something.

#     Warning:
#         Rules have not yet been implemented. They will likely have a similar API to Codes, although this is yet to be determined. In particular, a Rule will be designed to be a base class for specific types of Rule, while there is only one type of Code.

#     """

#     def __init__(self, name, xpath_base, case):
#         """Initialise a Rule."""
#         self.name = name
#         self.xpath_base = xpath_base
#         self.case = case


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """

    pass


# class RuleAtLeastOne(Rule):
#     """Representation of a Rule that checks that there is at least one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     def implementation(self, dataset):
#         """Check activity has at least one instance of a given case."""
#         pass


# class RuleDependent(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleSum(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleDateOrder(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleRegexMatches(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleRegexNoMatches(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleStartsWith(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass


# class RuleUnique(Rule):
#     """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

#     Warning:
#         Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

#         The name of specific types of Rule may better indicate that they are Rules.

#     """

#     pass
