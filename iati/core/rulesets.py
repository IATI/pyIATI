"""A module containg a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Todo:
    Account for edge cases and improve documentation.

"""
import re
import time
import json
import sre_constants
import jsonschema
import iati.core.default
import iati.core.utilities


_VALID_RULE_TYPES = ["atleast_one", "dependent", "sum", "date_order", "no_more_than_one", "regex_matches", "regex_no_matches", "startswith", "unique"]


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
        This is only external to Ruleset to help with testing. Changing code to make testing easier is smelly.

    """
    possible_rule_types = {
        'atleast_one': RuleAtLeastOne,
        'date_order': RuleDateOrder,
        'dependent': RuleDependent,
        'no_more_than_one': RuleNoMoreThanOne,
        'regex_matches': RuleRegexMatches,
        'regex_no_matches': RuleRegexNoMatches,
        'startswith': RuleStartsWith,
        'sum': RuleSum,
        'unique': RuleUnique
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
            Raises a UnicodeDecodeError or json.JSONDecodeError if passed a dodgey bytearray in all Python versions except 3.6.

        """
        self.ruleset = json.loads(ruleset_str, object_pairs_hook=iati.core.utilities.dict_raise_on_duplicates)
        self.validate_ruleset()
        self.rules = set()
        self.set_rules()

    def validate_ruleset(self):
        """Validate a Ruleset against the Ruleset Schema."""
        try:
            jsonschema.validate(self.ruleset, iati.core.default.ruleset_schema())
        except jsonschema.ValidationError:
            raise ValueError

    def set_rules(self):
        """Set the Rules of the Ruleset."""
        try:
            for xpath_base, rule in self.ruleset.items():
                for rule_type, cases in rule.items():
                    for case in cases['cases']:
                        constructor = locate_constructor_for_rule_type(rule_type)
                        new_rule = constructor(xpath_base, case)
                        self.rules.add(new_rule)
        except ValueError:
            raise


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually check the content of the data.

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
        self.case = case
        self.xpath_base = xpath_base
        self._valid_rule_configuration(case)
        self._set_case_attributes(case)
        self._normalize_xpaths()

    def _normalize_xpath(self, path):
        """Normalize a single xpath by combining it with `xpath_base`.

        Error:
            Raises an attribute error if self.xpath_base
            isn't set.

        Todo:
            Add some logging.

        """
        if path == '':
            return self.xpath_base
        return self.xpath_base + '/' + path

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `xpath_base`.

        Todo:
            Discuss appropriate edge cases and what is going on here.

        """
        # try:
        self.paths = [self._normalize_xpath(path) for path in self.paths]
        # except AttributeError:
        #     pass

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

    def _set_case_attributes(self, case):
        """Make the required attributes within a case their own attributes in the class.

        Args:
            case (dict): The case to take values from.

        Todo:
            Set non-required properties such as a `condition`.
        """
        required_attributes = self._required_case_attributes(self._ruleset_schema_section())
        for attrib in required_attributes:
            setattr(self, attrib, case[attrib])

    def _required_case_attributes(self, partial_schema):
        """Determine the attributes that must be present given the Schema for the Rule type.

        Args:
            partial_schema (dict): The partial JSONSchema to extract attribute names from.

        Returns:
            list of str: The names of required attributes.

        """
        return [key for key in partial_schema['properties'].keys() if key != 'condition']

    def _ruleset_schema_section(self):
        """Locate the section of the Ruleset Schema relevant for the Rule.

        In doing so, makes required properties required.

        Returns:
            dict: A dictionary of the relevant part of the Ruleset Schema, based on the Rule's name.

        Raises:
            AttributeError: When the Rule's name is unset or not a permitted rule_type.

        """
        ruleset_schema = iati.core.default.ruleset_schema()
        partial_schema = ruleset_schema['patternProperties']['.+']['properties'][self.name]['properties']['cases']['items']  # pylint: disable=E1101
        # make all attributes other than 'condition' in the partial schema required
        partial_schema['required'] = self._required_case_attributes(partial_schema)
        # ensure that the 'paths' array is not empty
        if 'paths' in partial_schema['properties'].keys():
            partial_schema['properties']['paths']['minItems'] = 1

        return partial_schema


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath."""

    def __init__(self, xpath_base, case):
        """Initialise an `atleast_one` rule."""
        self.name = "atleast_one"

        super(RuleAtLeastOne, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Check `dataset.xml_tree` has at least one instance of a given case for an Element.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            Boolean value that changes depending on whether the case is found in the dataset.xml_tree.

        """
        for path in self.paths:
            return dataset.xml_tree.find(path) is not None  # is this doing what is wanted?


class RuleDateOrder(Rule):
    """Representation of a Rule that checks that the date value of `more` is the most recent value in comparison to the date value of `less`."""

    def __init__(self, xpath_base, case):
        """Initialise a `date_order` rule."""
        self.name = "date_order"
        self.special_case = 'NOW'  # Was a constant sort of

        super(RuleDateOrder, self).__init__(xpath_base, case)

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `xpath_base`."""
        if self.less is not self.special_case:
            self.less = self._normalize_xpath(self.less)

        if self.more is not self.special_case:
            self.more = self._normalize_xpath(self.more)

    def is_valid_for(self, dataset):
        """Assert that the date value of `less` is older than the date value of `more`.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Return:
            A boolean value. If `less` is older than `more`, return `True`.

        """
        less_date = dataset.xml_tree.xpath(self.less)
        more_date = dataset.xml_tree.xpath(self.more)
        earlier_date = time.strptime(less_date[0], '%Y-%m-%d')
        later_date = time.strptime(more_date[0], '%Y-%m-%d')

        return earlier_date < later_date


class RuleDependent(Rule):
    """Representation of a Rule that checks that if one of the elements in a given `path` exists then all its dependent paths must also exist."""

    def __init__(self, xpath_base, case):
        """Initialise a `dependent` rule."""
        self.name = "dependent"

        super(RuleDependent, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Assert that either all given `paths` or none of the given `paths` exist in a dataset.xml_tree.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If no `paths`, or all `paths` are found in the dataset.xml_tree, return `True`.

        """
        found_paths = 0

        for path in self.paths:
            result = dataset.xml_tree.findall(path)
            if result != list():
                found_paths += 1

        return not found_paths or found_paths == len(self.paths)


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath."""

    def __init__(self, xpath_base, case):
        """Initialise a `no_more_than_one` rule."""
        self.name = "no_more_than_one"

        super(RuleNoMoreThanOne, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Check `dataset.xml_tree` has no more than one instance of a given case for an Element.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            Boolean value that changes depending on whether one or fewer cases are found in the dataset.xml_tree.

        """
        for path in self.paths:
            return len(dataset.xml_tree.findall(path)) <= 1  # is this doing what is wanted?


class RuleRegexMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must contain values that match the `regex` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `regex_matches` rule."""
        self.name = "regex_matches"

        super(RuleRegexMatches, self).__init__(xpath_base, case)

        try:
            re.compile(case['regex'])
        except sre_constants.error:
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that the text of the given `paths` matches the `regex` value.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If the text of the given `path` matches the `regex` value, return `True`.

        """
        pattern = re.compile(self.case['regex'])

        for path in self.paths:
            results = dataset.xml_tree.findall(path)
            for result in results:
                return bool(pattern.match(result.text))


class RuleRegexNoMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must not contain values that match the `regex` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `regex_no_matches` rule."""
        self.name = "regex_no_matches"

        super(RuleRegexNoMatches, self).__init__(xpath_base, case)

        try:
            re.compile(case['regex'])
        except sre_constants.error:
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that no text of the given `paths` matches the `regex` value.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If the text of the given `path` does not match the `regex` value, return `True`.

        """
        pattern = re.compile(self.case['regex'])

        for path in self.paths:
            results = dataset.xml_tree.findall(path)
            for result in results:
                return not bool(pattern.match(result.text))


class RuleStartsWith(Rule):
    """Representation of a Rule that checks that the start of each `path` text value matches the `start` text value.

    Todo:
        Test with multiple start strings (should error).

    """

    def __init__(self, xpath_base, case):
        """Initialise a `startswith` rule."""
        self.name = "startswith"

        super(RuleStartsWith, self).__init__(xpath_base, case)

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `xpath_base`."""
        super(RuleStartsWith, self)._normalize_xpaths()

        self.start = self._normalize_xpath(self.start)

    def is_valid_for(self, dataset):
        """Assert that the prefixing text of all given `paths` starts with the text of `start`.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If the `path` string starts with the `start` string, return `True`.

        """
        prefixing_str = dataset.xml_tree.xpath(self.start)

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                el_str = result.text
                return el_str.startswith(prefixing_str[0])


class RuleSum(Rule):
    """Representation of a Rule that checks that the values in given `path` attributes must sum to the given `sum` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `sum` rule."""
        self.name = "sum"

        super(RuleSum, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Assert that the total of the values given in `paths` match the given `sum` value.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If the `path` values total to the `sum` value, return `True`.

        """
        sum_values = list()

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                sum_values.append(float(result))

        total = sum(sum_values)

        return total == self.sum  # pylint: disable=no-member


class RuleUnique(Rule):
    """Representation of a Rule that checks that the text of each given path must be unique."""

    def __init__(self, xpath_base, case):
        """Initialise a `unique` rule."""
        self.name = "unique"

        super(RuleUnique, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Assert that the given paths are not found in the dataset.xml_tree more than once.

        Args:
            dataset.xml_tree: an etree created from an XML dataset.

        Returns:
            A boolean value. If no repeated text is found in the dataset.xml_tree for the given paths the value returned will be `True`.

        Todo:
            Consider better methods for specifying which elements in the tree contain non-permitted duplication, such as bucket sort.
            Test with a test ruleset that has multiple paths.

        """
        original = list()
        unique = set()

        for path in self.paths:
            results = dataset.xml_tree.findall(path)
            for result in results:
                original.append(result.text)
                unique.add(result.text)

        return len(original) == len(unique)
