"""A module containg a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Warning:
    The contents of this module have not been implemented. Their structure may change when they are implemented.

Todo:
    Implement Rulesets (and Rules). Likely worth completing the Codelist implementation first since the two will be similar.

"""
import json
import jsonschema
import six
import iati.core.default
import iati.core.utilities


_VALID_RULE_TYPES = ["no_more_than_one", "atleast_one", "dependent", "sum", "date_order", "regex_matches", "regex_no_matches", "startswith", "unique"]


def locate_constructor_for_rule_type(rule_type):
    """Locate the constructor for specific rule types.

    Args:
        rule_type (str): The name of the type of Rule to identify the class for.

    Returns:
        Rule implementation: A constructor for a class that inherits from Rule.

    Raises:
        KeyError: When a non-permitted `rule_type` is provided.

    Todo:
        Determine scope of this function, and how much testing is therefore required.

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
            ValueError: When ruleset_str does not validate against the ruleset schema.

        Todo:
            May raise a UnicodeDecodeError or json.JSONDecodeError if passed a dodgey bytearray. Need to test.

        """
        ruleset = json.loads(ruleset_str, object_pairs_hook=iati.core.utilities.dict_raise_on_duplicates)

        try:
            jsonschema.validate(ruleset, iati.core.default.ruleset_schema())
        except jsonschema.ValidationError:
            raise ValueError
        self.rules = set()

        for xpath_base, rule in ruleset.items():
            for rule_type, cases in rule.items():
                for case in cases['cases']:
                    constructor = locate_constructor_for_rule_type(rule_type)
                    new_rule = constructor(xpath_base, case)
                    self.rules.add(new_rule)


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually do something.

    Todo:
        Determine whether this should be an Abstract Base Class.

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

        self._valid_rule_configuration(case)

        self.xpath_base = xpath_base

    def _valid_rule_configuration(self, case):
        """Check that a configuration being passed into a Rule is valid for the given type of Rule.

        Note:
            The `name` attribute on the class must be set to a valid rule_type before this function is called.

        Args:
            case (dict): A dictionary of values, generally parsed as a case from a Ruleset.

        Raises:
            AttributeError: When the Rule's name is unset or not a permitted rule_type.
            ValueError: When the case is not valid for the type of Rule.

        """
        try:
            ruleset_schema_section = self._ruleset_schema_section()
        except AttributeError:
            raise

        try:
            jsonschema.validate(case, ruleset_schema_section)
        except jsonschema.ValidationError:
            raise ValueError

    def _ruleset_schema_section(self):
        """Locate the section of the Ruleset Schema relevant for the Rule.

        In doing so, makes required properties required.

        Returns:
            dict: A dictionary of the relevant part of the Ruleset Schema, based on the Rule's name.

        Raises:
            AttributeError: When the Rule's name is unset or not a permitted rule_type.

        """
        ruleset_schema = iati.core.default.ruleset_schema()
        partial_schema = ruleset_schema['patternProperties']['.+']['properties'][self.name]['properties']['cases']['items']
        partial_schema['required'] = [key for key in partial_schema['properties'].keys() if key != 'condition']

        return partial_schema


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """
    def __init__(self, xpath_base, case):
        self.name = "no_more_than_one"

        super(RuleNoMoreThanOne, self).__init__(xpath_base, case)


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath.

    Warning:
        Rules have not yet been implemented. The structure of specific types of Rule will depend on how the base class is formed.

        The name of specific types of Rule may better indicate that they are Rules.

    """
    def __init__(self, xpath_base, case):
        self.name = "atleast_one"

        super(RuleAtLeastOne, self).__init__(xpath_base, case)

    def implementation(self, dataset):
        """Check activity has at least one instance of a given case."""
        pass
