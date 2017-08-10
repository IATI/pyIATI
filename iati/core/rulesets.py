"""A module containing a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Todo:
    Review for edge cases.
    Consider how we should handle lxml errors.

"""
from datetime import datetime
import json
import re
import six
import sre_constants
import jsonschema
import iati.core.default
import iati.core.utilities


_VALID_RULE_TYPES = ["atleast_one", "dependent", "sum", "date_order", "no_more_than_one", "regex_matches", "regex_no_matches", "startswith", "unique"]


def locate_constructor_for_rule_type(rule_type):
    """Locate the constructor for specific Rule types.

    Args:
        rule_type (str): The name of the type of Rule to identify the class for.

    Returns:
        type: A constructor for a class that inherits from Rule.

    Raises:
        KeyError: When a non-permitted `rule_type` is provided.

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
            TypeError: When a `ruleset_str` is not a string.
            ValueError: When a `ruleset_str` does not validate against the Ruleset Schema or cannot be correctly decoded.

        """
        try:
            self.ruleset = json.loads(ruleset_str, object_pairs_hook=iati.core.utilities.dict_raise_on_duplicates)
        except TypeError:
            raise ValueError
        self.validate_ruleset()
        self.rules = set()
        self._set_rules()

    def validate_ruleset(self):
        """Validate a Ruleset against the Ruleset Schema.

        Raises:
            ValueError: When `ruleset_str` does not validate against the Ruleset Schema.

        """
        try:
            jsonschema.validate(self.ruleset, iati.core.default.ruleset_schema())
        except jsonschema.ValidationError:
            raise ValueError

    def _set_rules(self):
        """Set the Rules of the Ruleset.

        Extract each case of each Rule from the Ruleset and add to initialised `rules` set.

        """
        for xpath_base, rule in self.ruleset.items():
            for rule_type, cases in rule.items():
                for case in cases['cases']:
                    constructor = locate_constructor_for_rule_type(rule_type)
                    new_rule = constructor(xpath_base, case)
                    self.rules.add(new_rule)


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually check the content of the data.

    Todo:
        Determine whether this should be an Abstract Base Class.
        Standardise normalized paths.

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
        self.xpath_base = self._valid_xpath_base(xpath_base)
        self._valid_rule_configuration(case)
        self._set_case_attributes(case)
        self._normalize_xpaths()

    def _valid_xpath_base(self, xpath_base):
        """Check that a valid `xpath_base` is given for a Rule.

        Args:
            xpath_base(str): The root of an XPath query.

        Returns:
            str: A valid XPath root.

        Raises:
            TypeError: When an argument is given that is not a string.

        """
        if isinstance(xpath_base, six.string_types):
            return xpath_base
        raise TypeError

    def _normalize_xpath(self, path):
        """Normalize a single XPath by combining it with `xpath_base`.

        Args:
            path(str): An XPath.

        Raises:
            AttributeError: When the `xpath_base` isn't set.

        Todo:
            Add some logging.

        """
        if path == '':
            return self.xpath_base
        return '/'.join([self.xpath_base, path])

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `xpath_base`.

        May be overridden in child class that does not use `paths`.

        """
        self.paths = [self._normalize_xpath(path) for path in self.paths]

    def _valid_rule_configuration(self, case):
        """Check that a configuration being passed into a Rule is valid for the given type of Rule.

        Args:
            case (dict): A dictionary of values, generally parsed as a case from a Ruleset.

        Raises:
            AttributeError: When the Rule name is unset or does not have the required attributes.
            ValueError: When the case is not valid for the type of Rule.

        Note:
            The `name` attribute on the class must be set to a valid rule_type before this function is called.

        """
        try:
            jsonschema.validate(case, self._ruleset_schema_section())
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
            AttributeError: When the Rule name is unset or does not have the required attributes.

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
        """Check Dataset has at least one instance of a given case for an Element.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the case is found in the Dataset.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        """
        found_paths = set()

        for path in self.paths:
            if dataset.xml_tree.xpath(path) != list():
                found_paths.add(path)
        return len(found_paths) == len(self.paths)


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
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Return:
            bool: Return `True` when `less` is chronologically before `more`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            ValueError: When a date is given that is not in the correct xsd:date format.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        Note:
            `date` restricted to 10 characters in order to exclude possible timezone values.

        """
        less_date = dataset.xml_tree.xpath(self.less)
        more_date = dataset.xml_tree.xpath(self.more)
        earlier_dates = list()
        later_dates = list()

        for date in less_date:
            if date == 'NOW':
                earlier_dates.append(datetime.strptime(datetime.today(), '%Y-%m-%d'))
            earlier_dates.append(datetime.strptime(date[:10], '%Y-%m-%d'))

        for date in more_date:
            if date == 'NOW':
                later_dates.append(datetime.today())
            else:
                later_dates.append(datetime.strptime(date[:10], '%Y-%m-%d'))

        for (early_date, later_date) in zip(earlier_dates, later_dates):
            if early_date > later_date:
                return False

        return True


class RuleDependent(Rule):
    """Representation of a Rule that checks that if one of the elements in a given `path` exists then all its dependent paths must also exist."""

    def __init__(self, xpath_base, case):
        """Initialise a `dependent` rule."""
        self.name = "dependent"

        super(RuleDependent, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Assert that either all given `paths` or none of the given `paths` exist in a Dataset.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when all dependent `paths` are found in the Dataset, if any exist.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        """
        found_paths = 0

        for path in self.paths:
            result = dataset.xml_tree.xpath(path)
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
        """Check dataset has no more than one instance of a given case for an Element.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when one or fewer cases are found in the Dataset.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        """
        compliant_paths = set()

        for path in self.paths:
            if len(dataset.xml_tree.xpath(path)) <= 1:
                compliant_paths.add(path)

        return len(compliant_paths) == len(self.paths)


class RuleRegexMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must contain values that match the `regex` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `regex_matches` Rule.

        Raises:
            ValueError: When the case does not contain a valid regex.

        """
        self.name = "regex_matches"

        super(RuleRegexMatches, self).__init__(xpath_base, case)

        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that the text of the given `paths` matches the `regex` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the given `path` text matches the given regex case.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        """
        pattern = re.compile(self.case['regex'])

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                return bool(pattern.match(result.text))


class RuleRegexNoMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must not contain values that match the `regex` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `regex_no_matches` Rule.

        Raises:
            ValueError: When the case does not contain a valid regex.

        """
        self.name = "regex_no_matches"

        super(RuleRegexNoMatches, self).__init__(xpath_base, case)

        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that no text of the given `paths` matches the `regex` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the given `path` text does not match the given regex case.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        """
        pattern = re.compile(self.case['regex'])

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                return not bool(pattern.match(result.text))


class RuleStartsWith(Rule):
    """Representation of a Rule that checks that the start of each `path` text value matches the `start` text value.

    Todo:
        Test with multiple start strings (should error).

    """

    def __init__(self, xpath_base, case):
        """Initialise a `startswith` Rule."""
        self.name = "startswith"

        super(RuleStartsWith, self).__init__(xpath_base, case)

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `xpath_base`."""
        super(RuleStartsWith, self)._normalize_xpaths()

        self.start = self._normalize_xpath(self.start)

    def is_valid_for(self, dataset):
        """Assert that the prefixing text of all given `paths` starts with the text of `start`.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the `path` text starts with the value of `start`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            IndexError: When XPath query result is not iterable.

        """
        prefixing_str = dataset.xml_tree.xpath(self.start)[0]

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                element_string = result.text
                return element_string.startswith(prefixing_str)


class RuleSum(Rule):
    """Representation of a Rule that checks that the values in given `path` attributes must sum to the given `sum` value."""

    def __init__(self, xpath_base, case):
        """Initialise a `sum` rule."""
        self.name = "sum"

        super(RuleSum, self).__init__(xpath_base, case)

    def is_valid_for(self, dataset):
        """Assert that the total of the values given in `paths` match the given `sum` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the `path` values total to the `sum` value.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

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
        """Assert that the given `paths` are not found in the dataset.xml_tree more than once.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when repeated text is found in the dataset for the given `paths`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            XPathEvalError(lxml.etree.XPathEvalError): When no valid XPath is available.

        Todo:
            Consider better methods for specifying which elements in the tree contain non-permitted duplication, such as bucket sort.

        """
        original = list()
        unique = set()

        for path in self.paths:
            results = dataset.xml_tree.xpath(path)
            for result in results:
                original.append(result.text)
                unique.add(result.text)

        return len(original) == len(unique)
