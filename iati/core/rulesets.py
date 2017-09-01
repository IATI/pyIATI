"""A module containing a core representation of IATI Rulesets.

Note:
    Rulesets are under-implemented since it is expected that their implementation will be similar to that of Codelists, which is currently unstable. Once Codelist stability has been increased, Rulesets may be fully-implemented.

Todo:
    Review for edge cases.
    Consider how we should handle lxml errors.
    Remove references to `case`.

"""
from datetime import datetime
import json
import re
import sre_constants
from decimal import Decimal
import jsonschema
# import lxml
import six
import iati.core.default
import iati.core.utilities


_VALID_RULE_TYPES = ["atleast_one", "dependent", "sum", "date_order", "no_more_than_one", "regex_matches", "regex_no_matches", "startswith", "unique"]


def constructor_for_rule_type(rule_type):
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
        for context, rule in self.ruleset.items():
            for rule_type, cases in rule.items():
                for case in cases['cases']:
                    constructor = constructor_for_rule_type(rule_type)
                    new_rule = constructor(context, case)
                    self.rules.add(new_rule)


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually check the content of the data.

    Todo:
        Determine whether this should be an Abstract Base Class.

    """

    def __init__(self, context, case):
        """Initialise a Rule.

        Args:
            context (str): The base of the XPath that the Rule will act upon.
            case (dict): Specific configuration for this instance of the Rule.

        Raises:
            TypeError: When a parameter is of an incorrect type.
            ValueError: When a rule_type is not one of the permitted Rule types.

        """
        self.case = case
        self.context = self._validated_context(context)
        self._valid_rule_configuration(case)
        self._set_case_attributes(case)
        self._normalize_xpaths()

    def _validated_context(self, context):
        """Check that a valid `context` is given for a Rule.

        Args:
            context (str): The XPath expression that selects XML elements that the Rule acts against.

        Returns:
            str: A valid XPath.

        Raises:
            TypeError: When an argument is given that is not a string.
            ValueError: When `context` is an empty string.

        """
        if isinstance(context, six.string_types):
            if context != '':
                return context
            raise ValueError
        raise TypeError

    def _normalize_xpath(self, path):
        """Normalize a single XPath by combining it with `context`.

        Args:
            path (str): An XPath.

        Raises:
            AttributeError: When the `context` isn't set.
            ValueError: When `path` is an empty string.

        Todo:
            Add some logging.
            Re-evaluate this.

        """
        if path == '':
            raise ValueError
        return '/'.join([self.context, path])

    def _normalize_condition(self):
        """Normalize `condition` xpaths."""
        try:
            self.normalized_paths.append(self._normalize_xpath(self.condition))
        except AttributeError:
            pass

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `context`.

        Note:
            May be overridden in child class that does not use `paths`.

        """
        self.normalized_paths = [self._normalize_xpath(path) for path in self.paths]
        self._normalize_condition()

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
        required_attributes = self._case_attributes(self._ruleset_schema_section())
        for attrib in required_attributes:
            setattr(self, attrib, case[attrib])

        optional_attributes = self._case_attributes(self._ruleset_schema_section(), False)
        for attrib in optional_attributes:
            try:
                setattr(self, attrib, case[attrib])
            except KeyError:
                pass

    def _case_attributes(self, partial_schema, required=True):
        """Determine the attributes that must be present given the Schema for the Rule type.

        Args:
            partial_schema (dict): The partial JSONSchema to extract attribute names from.
            required (bool): Specifies whether the attributes to be returned should be required or optional according to the Ruleset specification.

        Returns:
            list of str: The names of required or optional attributes.

        """
        if required:
            return [key for key in partial_schema['properties'].keys() if key != 'condition']
        return [key for key in partial_schema['properties'].keys() if key == 'condition']

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
        partial_schema['required'] = self._case_attributes(partial_schema)
        # ensure that the 'paths' array is not empty
        if 'paths' in partial_schema['properties'].keys():
            partial_schema['properties']['paths']['minItems'] = 1

        return partial_schema

    def _find_context_elements(self, dataset):
        """Find the specific elements in context for the Rule.

        Args:
            dataset (iati.core.Dataset): The Dataset to be chacked for validity against the Rule.

        Returns:
            list of elements: Results of XPath query.

        """
        return dataset.xml_tree.xpath(self.context)

    def _extract_text_from_element_or_attribute(self, context, path):
        """Return a list of strings regardless of whether XPath result is an attribute or an element.

        Args:
            context (Element): An xml Element.
            path (str): An XPath query string.

        Returns:
            list of str: Text values from XPath query results.

        Note:
            `Element.text` will return `None` if it contains no text. This is bad. As such, this is converted to an empty string to prevent TypeErrors.

        """
        xpath_results = context.xpath(path)
        results = [result if isinstance(result, six.string_types) else result.text for result in xpath_results]
        return ['' if result is None else result for result in results]

    def _condition_met_for(self, context_element):
        """Check for condtions of a given case.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against a Rule.

        Returns:
            bool: Returns `False` when condition not met.
                  Returns `True` when condition is met.
            None: Returns `None` when condition met.

        Warning:
            Current implementation may be vulnerable to XPath injection vulnerabilities.

        Todo:
            Need to assess the possibility of risk and potential counter-measures/avoidance strategies if needed.
            Need to decide whether the implementation of this in Rules should `return None` or `continue`.
            Rename function to sound more truthy.

        """
        try:
            if context_element.xpath(self.condition):
                return True
        except AttributeError:
            return False

        return False


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath."""

    def __init__(self, context, case):
        """Initialise an `atleast_one` rule."""
        self.name = 'atleast_one'

        super(RuleAtLeastOne, self).__init__(context, case)

    def is_valid_for(self, dataset):
        """Check Dataset has at least one instance of a given case for an Element.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the case is found in the Dataset.
                  Return `False` when the case is not found in the Dataset.
            None: When a condition is met to skip validation.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        Todo:
            Check test data.

        """
        context_elements = self._find_context_elements(dataset)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            for path in self.paths:
                if context_element.xpath(path):
                    return True

        return False


class RuleDateOrder(Rule):
    """Representation of a Rule that checks that the date value of `more` is the most recent value in comparison to the date value of `less`."""

    def __init__(self, context, case):
        """Initialise a `date_order` rule."""
        self.name = 'date_order'
        self.special_case = 'NOW'  # Was a constant sort of

        super(RuleDateOrder, self).__init__(context, case)

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `context`."""
        self.normalized_paths = list()
        if self.less is not self.special_case:
            self.normalized_paths.append(self._normalize_xpath(self.less))

        if self.more is not self.special_case:
            self.normalized_paths.append(self._normalize_xpath(self.more))

        self._normalize_condition()

    def is_valid_for(self, dataset):
        """Assert that the date value of `less` is older than the date value of `more`.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Return:
            bool: Return `True` when `less` is chronologically before `more`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.
            ValueError: When a date is given that is not in the correct xsd:date format.

        Note:
            `date` restricted to 10 characters in order to exclude possible timezone values.

        """
        def get_date(context, path):
            """Retrieve datetime object from an XPath string.

            Args:
                context (an XPath): For the context in which further XPath queries are then made.
                path: (an XPath): The ultimate XPath query to find the desired elements.

            Returns:
                datetime.datetime: A datetime object.

            Raises:
                ValueError:
                    When a non-permitted number of unique dates are given for a `less` or `more` value.
                    When datetime cannot convert a string of non-permitted characters.
                    When non-permitted trailing characters are found after the core date string characters.

            Note:
                Though technically permitted, any dates with a leading '-' character are almost certainly incorrect and are therefore treated as data errors.

            Todo:
                Consider breaking this function down further so it follows SRP.

            """
            if path == self.special_case:
                return datetime.today()

            dates = self._extract_text_from_element_or_attribute(context, path)
            if not dates[0]:
                return
            # Checks that anything after the YYYY-MM-DD string is a permitted timezone character
            pattern = re.compile(r'^([+-]([01][0-9]|2[0-3]):([0-5][0-9])|Z)?$')
            if (len(set(dates)) == 1) and pattern.match(dates[0][10:]):
                return datetime.strptime(dates[0][:10], '%Y-%m-%d')
            raise ValueError

        context_elements = self._find_context_elements(dataset)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            early_date = get_date(context_element, self.less)
            later_date = get_date(context_element, self.more)

            try:
                # python2 allows `bool`s to be compared to `None` without raising a TypeError, while python3 does not
                if early_date is None or later_date is None:
                    return None

                if early_date >= later_date:
                    return False
            except TypeError:
                # a TypeError is raised in python3 if either of the dates is None
                return None

        return True


class RuleDependent(Rule):
    """Representation of a Rule that checks that if one of the elements in a given `path` exists then all its dependent paths must also exist."""

    def __init__(self, context, case):
        """Initialise a `dependent` rule."""
        self.name = 'dependent'

        super(RuleDependent, self).__init__(context, case)

    def is_valid_for(self, dataset):
        """Assert that either all given `paths` or none of the given `paths` exist in a Dataset.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when all dependent `paths` are found in the Dataset, if any exist.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        Todo:
            Determine if it's reasonable to assume the user should give a specific xpath format, or whether the context-path structure dictates automatic conversion to relative paths.

        """
        def add_query_result(result):
            """Add appropriate result to `found_in_dataset` whether attribute or element.

            Args:
                result (XPath element or attribute string): An XPath return value.

            Todo:
                Maybe refactor to return tag instead and extract to Rule base class.

            """
            try:
                if result.is_attribute:
                    found_in_dataset.add(result.getparent().tag)
            except AttributeError:
                found_in_dataset.add(result.tag)

        context_elements = self._find_context_elements(dataset)
        paths = set(self.paths)
        found_in_dataset = set()

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            for path in paths:
                results = context_element.xpath(path)
                for result in results:
                    # result will be an empty list when no elements or attribute text is found
                    if result != list():
                        add_query_result(result)

        return not found_in_dataset or len(found_in_dataset) == len(paths)


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath."""

    def __init__(self, context, case):
        """Initialise a `no_more_than_one` rule."""
        self.name = 'no_more_than_one'

        super(RuleNoMoreThanOne, self).__init__(context, case)

    def is_valid_for(self, dataset):
        """Check dataset has no more than one instance of a given case for an Element.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when one or fewer cases are found in the Dataset.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        Todo:
            Check test data.

        """
        context_elements = self._find_context_elements(dataset)
        paths = set(self.paths)
        compliant_paths = list()
        no_of_paths = 0

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            no_of_paths += len(paths)
            for path in paths:
                results = context_element.xpath(path)
                if len(results) <= 1:
                    compliant_paths.append(path)

        return len(compliant_paths) == no_of_paths


class RuleRegexMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must contain values that match the `regex` value."""

    def __init__(self, context, case):
        """Initialise a `regex_matches` Rule.

        Raises:
            ValueError: When the case does not contain valid regex.

        """
        self.name = 'regex_matches'

        super(RuleRegexMatches, self).__init__(context, case)

        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError
        if self.regex == '':
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that the text of the given `paths` matches the `regex` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the given `path` text matches the given regex case.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        """
        context_elements = self._find_context_elements(dataset)
        pattern = re.compile(self.regex)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            for path in self.paths:
                strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
                for string_to_check in strings_to_check:
                    if not pattern.search(string_to_check):
                        return False
                    continue

        return True


class RuleRegexNoMatches(Rule):
    """Representation of a Rule that checks that the given `paths` must not contain values that match the `regex` value."""

    def __init__(self, context, case):
        """Initialise a `regex_no_matches` Rule.

        Raises:
            ValueError: When the case does not contain valid regex.

        """
        self.name = 'regex_no_matches'

        super(RuleRegexNoMatches, self).__init__(context, case)

        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError
        if self.regex == '':
            raise ValueError

    def is_valid_for(self, dataset):
        """Assert that no text of the given `paths` matches the `regex` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the given `path` text does not match the given regex case.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        """
        context_elements = self._find_context_elements(dataset)
        pattern = re.compile(self.regex)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            for path in self.paths:
                strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
                for string_to_check in strings_to_check:
                    if pattern.search(string_to_check):
                        return False
                    continue

        return True


class RuleStartsWith(Rule):
    """Representation of a Rule that checks that the start of each `path` text value matches the `start` text value."""

    def __init__(self, context, case):
        """Initialise a `startswith` Rule."""
        self.name = 'startswith'

        super(RuleStartsWith, self).__init__(context, case)

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `context`."""
        super(RuleStartsWith, self)._normalize_xpaths()

        self.normalized_paths.append(self._normalize_xpath(self.start))

    def is_valid_for(self, dataset):
        """Assert that the prefixing text of all given `paths` starts with the text of `start`.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the `path` text starts with the value of `start`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        """
        context_elements = self._find_context_elements(dataset)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            prefix = self._extract_text_from_element_or_attribute(context_element, self.start)[0]
            for path in self.paths:
                strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
                for string_to_check in strings_to_check:
                    if not string_to_check.startswith(prefix):
                        return False

        return True


class RuleSum(Rule):
    """Representation of a Rule that checks that the values in given `path` attributes must sum to the given `sum` value."""

    def __init__(self, context, case):
        """Initialise a `sum` rule."""
        self.name = 'sum'

        super(RuleSum, self).__init__(context, case)

    def is_valid_for(self, dataset):
        """Assert that the total of the values given in `paths` match the given `sum` value.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when the `path` values total to the `sum` value.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        """
        context_elements = self._find_context_elements(dataset)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None
            values_in_context = list()
            for path in set(self.paths):
                values_to_sum = self._extract_text_from_element_or_attribute(context_element, path)
                for value in values_to_sum:
                    values_in_context.append(Decimal(value))
            if sum(values_in_context) != Decimal(str(self.sum)):
                return False

        return True


class RuleUnique(Rule):
    """Representation of a Rule that checks that the text of each given path must be unique."""

    def __init__(self, context, case):
        """Initialise a `unique` rule."""
        self.name = 'unique'

        super(RuleUnique, self).__init__(context, case)

    def is_valid_for(self, dataset):
        """Assert that the given `paths` are not found in the dataset.xml_tree more than once.

        Args:
            dataset (iati.core.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool: Return `True` when repeated text is found in the dataset for the given `paths`.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        Todo:
            Consider better methods for specifying which elements in the tree contain non-permitted duplication, such as bucket sort.

        """
        context_elements = self._find_context_elements(dataset)

        unique_paths = set(self.paths)

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None

            all_content = list()
            unique_content = set()

            for path in unique_paths:
                strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
                for string_to_check in strings_to_check:
                    all_content.append(string_to_check)
                    unique_content.add(string_to_check)

            if len(all_content) != len(unique_content):
                return False

        return True
