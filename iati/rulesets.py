"""A module containing a core representation of IATI Rulesets.

Todo:
    Consider how we should handle lxml errors.

    Remove references to `case`.

"""
# no-member errors are due to using `setattr()` # pylint: disable=no-member
import decimal
import json
import re
import sre_constants
from datetime import datetime
import jsonschema
import six
import iati.default
import iati.utilities


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

    Attributes:
        rules (set): The Rules contained within this Ruleset.

    """

    def __init__(self, ruleset_str=None):
        """Initialise a Ruleset.

        Args:
            ruleset_str (str): A string that represents a Ruleset.

        Raises:
            TypeError: When `ruleset_str` is not a string.
            ValueError: When `ruleset_str` does not validate against the Ruleset Schema or cannot be correctly decoded.

        """
        self.rules = set()

        if ruleset_str is None:
            ruleset_str = ''

        try:
            ruleset_dict = json.loads(ruleset_str, object_pairs_hook=iati.utilities.dict_raise_on_duplicates)
        except TypeError:
            raise ValueError('Provided Ruleset string is not a string.')
        except ValueError:  # python2/3 - should be json.decoder.JSONDecodeError at python 3.5+
            if ruleset_str.strip() == '':
                ruleset_dict = {}
            else:
                raise ValueError('Provided Ruleset string is not valid JSON.')

        self._validate_ruleset(ruleset_dict)
        try:
            self._set_rules(ruleset_dict)
        except AttributeError:
            raise ValueError('Provided Ruleset validates against the Ruleset Schema, but should not. See: https://github.com/IATI/IATI-Rulesets/issues/49')

    def is_valid_for(self, dataset):
        """Validate a Dataset against the Ruleset.

        Args:
            Dataset (iati.Dataset): A Dataset to be checked for validity against the Ruleset.

        Returns:
            bool:
                `True` when the Dataset is valid against the Ruleset.

                `False` when part or all of the Dataset is not valid against the Ruleset.

        Todo:
            Better design how Skips and ValueErrors are treated. The current True/False/Skip/Error thing is a bit clunky.

        """
        for rule in self.rules:
            try:
                if rule.is_valid_for(dataset) is False:
                    return False
            except ValueError:
                return False

        return True

    def _validate_ruleset(self, ruleset_dict):
        """Validate a Ruleset against the Ruleset Schema.

        Args:
            ruleset_dict (dict): A JSON-format Ruleset parsed into a dictionary.

        Raises:
            ValueError: When `ruleset_dict` does not validate against the Ruleset Schema.

        """
        try:
            jsonschema.validate(ruleset_dict, iati.default.ruleset_schema())
        except jsonschema.ValidationError:
            raise ValueError('Provided Ruleset does not validate against the Ruleset Schema')

    def _set_rules(self, ruleset_dict):
        """Set the Rules of the Ruleset.

        Extract each case of each Rule from the Ruleset and add to initialised `rules` set.

        Args:
            ruleset_dict (dict): A JSON-format Ruleset parsed into a dictionary.

        """
        for context, rule in ruleset_dict.items():
            for rule_type, cases in rule.items():
                for case in cases['cases']:
                    constructor = constructor_for_rule_type(rule_type)
                    new_rule = constructor(context, case)
                    self.rules.add(new_rule)


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually check the content of the data.

    Attributes:
        context (str): An XPath expression to locate the elements that the Rule is to be checked against.
        case (dict): Specific configuration for this instance of the Rule.

    Todo:
        Determine whether this should be an Abstract Base Class.

    """

    def __init__(self, context, case):
        """Initialise a Rule.

        Args:
            case (dict): Specific configuration for this instance of the Rule.

        Raises:
            TypeError: When a parameter is of an incorrect type.
            ValueError: When a rule_type is not one of the permitted Rule types.

        """
        self._case = case
        self._context = self._validated_context(context)
        self._valid_rule_configuration(case)
        self._set_case_attributes(case)
        self._normalize_xpaths()

    def __str__(self):
        """Return string to state what the Rule is checking."""
        return 'This is a Rule.'

    def __eq__(self, other):
        """Check Rule equality.

        This allows uniqueness to be correctly defined upon insertion into a set.
        """
        return (self.name == other.name) and (str(self) == str(other))

    def __hash__(self):
        """Hash the Rule.

        This allows uniqueness to be correctly defined upon insertion into a set.
        """
        return hash((self.name, str(self)))

    @property
    def context(self):
        """str: An XPath expression to locate the elements that the Rule is to be checked against."""
        return self._context

    @property
    def name(self):
        """str: The type of Rule, as specified in a JSON Ruleset."""
        return self._name

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
        ruleset_schema = iati.default.ruleset_schema()
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
            dataset (iati.Dataset): The Dataset to be chacked for validity against the Rule.

        Returns:
            list of elements: Results of XPath query.

        Raises:
            AttributeError: When an argument is given that does not have the required attributes.

        """
        return dataset.xml_tree.xpath(self.context)

    def _extract_text_from_element_or_attribute(self, context, path):
        """Return a list of strings regardless of whether XPath result is an attribute or an element.

        Args:
            context (etree._Element): An xml Element.
            path (str): An XPath query string.

        Returns:
            list of str: Text values from XPath query results.

        Note:
            `Element.text` will return `None` if it contains no text. This is bad. As such, this is converted to an empty string to prevent TypeErrors.
            `path` should be validated outside of this function to avoid unexpected errors.

        """
        xpath_results = context.xpath(path)
        results = [result if isinstance(result, six.string_types) else result.text for result in xpath_results]
        return ['' if result is None else result for result in results]

    def _condition_met_for(self, context_element):
        """Check for condtions of a given case.

        Args:
            dataset (iati.Dataset): The Dataset to be checked for validity against a Rule.

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

    def is_valid_for(self, dataset):
        """Check whether a Dataset is valid against the Rule.

        Args:
            dataset (iati.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool or None:
                `True` when the Dataset is valid against the Rule.

                `False` when the Dataset is not valid against the Rule.

                `None` when a condition is met to skip validation.

        Raises:
            TypeError: When a Dataset is not given as an argument.
            ValueError: When a check encounters a completely incorrect value that it is unable to recover from within the definition of the Rule.

        Note:
            May be overridden in child class that does not have the same return structure for boolean results.

        Todo:
            Better design how Skips and ValueErrors are treated. The current True/False/Skip/Error thing is a bit clunky.

        """
        try:
            context_elements = self._find_context_elements(dataset)
        except AttributeError:
            raise TypeError

        if context_elements == list():
            return None

        for context_element in context_elements:
            if self._condition_met_for(context_element):
                return None

            rule_check_result = self._check_against_Rule(context_element)
            if rule_check_result is False:
                return False
            elif rule_check_result is None:
                return None

        return True


class RuleAtLeastOne(Rule):
    """Representation of a Rule that checks that there is at least one Element matching a given XPath.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.

    """

    def __init__(self, context, case):
        """Initialise an `atleast_one` rule."""
        self._name = 'atleast_one'

        super(RuleAtLeastOne, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleAtLeastOne is checking."""
        if len(self.paths) == 1:
            return '`{self.paths[0]}` must be present within each `{self.context}`.'.format(**locals())
        return 'At least one of `{0}` must be present within each `{self.context}`.'.format('` or `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Check `context_element` has at least one specified Element or Attribute.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `False` when the case is found in the Dataset.
                  Return `True` when the case is not found in the Dataset.

        """
        for path in self.paths:
            if context_element.xpath(path):
                return False
        return True

    def is_valid_for(self, dataset):
        """Check whether a Dataset is valid against the Rule.

        Args:
            dataset (iati.Dataset): The Dataset to be checked for validity against the Rule.

        Returns:
            bool or None:
                `True` when the Dataset is valid against the Rule.

                `False` when the Dataset is not valid against the Rule.

                `None` when a condition is met to skip validation.

        Raises:
            TypeError: When a Dataset is not given as an argument.

        """
        parent = super(RuleAtLeastOne, self).is_valid_for(dataset)

        if parent is True:
            return False
        elif parent is None:
            return None
        return True


class RuleDateOrder(Rule):
    """Representation of a Rule that checks that the date value of `more` is the most recent value in comparison to the date value of `less`.

    Attributes:
        less (str): An XPath expression to locate the element containing the date that should be in the past.
        more (str): An XPath expression to locate the element containing the date that should be in the future.
        special_case (str): A value that will be treated as the present when provided as the `less` or `more` value.

    """

    def __init__(self, context, case):
        """Initialise a `date_order` rule."""
        self._name = 'date_order'
        self.special_case = 'NOW'  # Was a constant sort of

        super(RuleDateOrder, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleDateOrder is checking."""
        if self.less == self.special_case and self.more == self.special_case:
            unformatted_str = '`{self.less}` must be chronologically before `{self.more}`. Try working that one out.'
        elif self.less == self.special_case:
            unformatted_str = '`{self.more}` must be in the future within each `{self.context}`.'
        elif self.more == self.special_case:
            unformatted_str = '`{self.less}` must be in the past within each `{self.context}`.'
        else:
            unformatted_str = '`{self.less}` must be chronologically before `{self.more}` within each `{self.context}`.'

        return unformatted_str.format(**locals())

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `context`."""
        self.normalized_paths = list()
        if self.less is not self.special_case:
            self.normalized_paths.append(self._normalize_xpath(self.less))

        if self.more is not self.special_case:
            self.normalized_paths.append(self._normalize_xpath(self.more))

        self._normalize_condition()

    def _get_date(self, context_element, path):
        """Retrieve datetime object from an XPath string.

        Args:
            context_element (etree._Element): An XML Element.
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
            Consider breaking this function down further.

        """
        if path == self.special_case:
            return datetime.today()

        dates = self._extract_text_from_element_or_attribute(context_element, path)
        if dates == list() or not dates[0]:
            return
        # Checks that anything after the YYYY-MM-DD string is a permitted timezone character
        pattern = re.compile(r'^([+-]([01][0-9]|2[0-3]):([0-5][0-9])|Z)?$')
        if (len(set(dates)) == 1) and pattern.match(dates[0][10:]):
            if len(dates[0]) < 10:
                # '%d' and '%m' are documented as requiring zero-padded dates.as input. This is actually for output. As such, a separate length check is required to ensure zero-padded values.
                raise ValueError
            return datetime.strptime(dates[0][:10], '%Y-%m-%d')
        raise ValueError

    def _check_against_Rule(self, context_element):
        """Assert that the date value of `less` is chronologically before the date value of `more`.

        Args:
            context_element (etree._Element): An XML Element.

        Return:
            bool: Return `True` when `less` is chronologically before `more`.
                  Return `False` when `less` is not chronologically before `more`.
            None: When a condition is met to skip validation.

        Raises:
            ValueError: When a date is given that is not in the correct xsd:date format.

        Note:
            `date` restricted to 10 characters in order to exclude possible timezone values.

        """
        early_date = self._get_date(context_element, self.less)
        later_date = self._get_date(context_element, self.more)

        try:
            # python2 allows `bool`s to be compared to `None` without raising a TypeError, while python3 does not
            if early_date is None or later_date is None:
                return None

            if early_date > later_date:
                return False
        except TypeError:
            # a TypeError is raised in python3 if either of the dates is None
            return None
        return True


class RuleDependent(Rule):
    """Representation of a Rule that checks that if one of the Elements or Attributes in a given `path` exists then all its dependent Elements or Attributes must also exist.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.

    """

    def __init__(self, context, case):
        """Initialise a `dependent` rule."""
        self._name = 'dependent'

        super(RuleDependent, self).__init__(context, case)

    def __str__(self):
        """Return string stating what TestRuleDependent is checking."""
        if len(self.paths) == 1:
            return 'Within each `{self.context}`, either `{self.paths[0]}` exists or it does not. As such, this Rule is always True.'.format(**locals())
        return 'Within each `{self.context}`, either none of `{0}` must exist, or they must all exist.'.format('` or `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Assert that either all given `paths` or none of the given `paths` exist for the `context_element`.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when all dependent `paths` are found in the Dataset, if any exist.
                  Return `False` when only some of the dependent `paths` are found in the Dataset.

        """
        unique_paths = set(self.paths)
        found_paths = 0
        for path in unique_paths:
            results = context_element.xpath(path)
            if results != list():
                found_paths += 1

        if found_paths not in [0, len(unique_paths)]:
            return False
        return True


class RuleNoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element or Attribute matching a given XPath.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.

    """

    def __init__(self, context, case):
        """Initialise a `no_more_than_one` rule."""
        self._name = 'no_more_than_one'

        super(RuleNoMoreThanOne, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleNoMoreThanOne is checking."""
        if len(self.paths) == 1:
            return '`{self.paths[0]}` must occur zero or one times within each `{self.context}`.'.format(**locals())
        return 'There must be no more than one element or attribute matched at `{0}` within each `{self.context}`.'.format('` or `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Check `context_element` has no more than one result for a specified Element or Attribute.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when one result or no results are found in the Dataset.
                  Return `False` when more than one result is found in the Dataset.

        """
        unique_paths = set(self.paths)

        found_elements = 0

        for path in unique_paths:
            results = context_element.xpath(path)
            found_elements += len(results)

        if found_elements > 1:
            return False
        return True


class RuleRegexMatches(Rule):
    """Representation of a Rule that checks that the text of the given paths must match the regex value.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.
        regex (str): A Perl-style regular expression.

    """

    def __init__(self, context, case):
        """Initialise a `regex_matches` Rule.

        Raises:
            ValueError: When the case does not contain valid regex.

        """
        self._name = 'regex_matches'

        super(RuleRegexMatches, self).__init__(context, case)

        if self.regex == '':
            raise ValueError
        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError

    def __str__(self):
        """Return string stating what RuleRegexMatches is checking."""
        if len(self.paths) == 1:
            return 'Each `{self.paths[0]}` within each `{self.context}` must match the regular expression `{self.regex}`.'.format(**locals())
        return 'Each instance of `{0}` within each `{self.context}` must match the regular expression `{self.regex}`.'.format('` and `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Assert that the text of the given `paths` matches the regex value.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when the given `path` text matches the given regex.
                  Return `False` when the given `path` text does not match the given regex.

        """
        pattern = re.compile(self.regex)

        for path in self.paths:
            strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
            for string_to_check in strings_to_check:
                if not pattern.search(string_to_check):
                    return False
        return True


class RuleRegexNoMatches(Rule):
    """Representation of a Rule that checks that the text of the given `paths` must not match the regex value.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.
        regex (str): A Perl-style regular expression.

    """

    def __init__(self, context, case):
        """Initialise a `regex_no_matches` Rule.

        Raises:
            ValueError: When the case does not contain valid regex.

        """
        self._name = 'regex_no_matches'

        super(RuleRegexNoMatches, self).__init__(context, case)

        if self.regex == '':
            raise ValueError
        try:
            re.compile(self.regex)
        except sre_constants.error:
            raise ValueError

    def __str__(self):
        """Return string stating what RuleRegexNoMatches is checking."""
        if len(self.paths) == 1:
            return 'Each `{self.paths[0]}` within each `{self.context}` must not match the regular expression `{self.regex}`.'.format(**locals())
        return 'Each instance of `{0}` within each `{self.context}` must not match the regular expression `{self.regex}`.'.format('` and `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Assert that no text of the given `paths` matches the regex value.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when the given `path` text does not match the given regex.
                  Return `False` when the given `path` text matches the given regex.

        """
        pattern = re.compile(self.regex)

        for path in self.paths:
            strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
            for string_to_check in strings_to_check:
                if pattern.search(string_to_check):
                    return False
        return True


class RuleStartsWith(Rule):
    """Representation of a Rule that checks that the prefixing text of each text value for `path` matches the `start` text value.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.
        start (str): An XPath expression to locate a single element. The text of this element is used as the prefix value for the Rule.

    """

    def __init__(self, context, case):
        """Initialise a `startswith` Rule."""
        self._name = 'startswith'

        super(RuleStartsWith, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleStartsWith is checking."""
        if len(self.paths) == 1:
            return 'Each `{self.paths[0]}` within each `{self.context}` must start with the value present at `{self.start}`.'.format(**locals())
        return 'Each instance of `{0}` within each `{self.context}` must start with the value present at `{self.start}`.'.format('` and `'.join(self.paths), **locals())

    def _normalize_xpaths(self):
        """Normalize xpaths by combining them with `context`."""
        super(RuleStartsWith, self)._normalize_xpaths()

        self.normalized_paths.append(self._normalize_xpath(self.start))

    def _check_against_Rule(self, context_element):
        """Assert that the prefixing text of all given `paths` starts with the text of `start`.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when the `path` text starts with the text value of `start`.
                  Return `False` when the `path` text does not start with the text value of `start`.

        Raises:
            ValueError: When more than one element or attribute is retured for the prefix value.
                        When no results are returned for the prefix value.

        """
        start_results = self._extract_text_from_element_or_attribute(context_element, self.start)

        if len(start_results) > 1:
            raise ValueError
        try:
            prefix = start_results[0]
        except IndexError:
            raise ValueError

        for path in self.paths:
            strings_to_check = self._extract_text_from_element_or_attribute(context_element, path)
            for string_to_check in strings_to_check:
                if not string_to_check.startswith(prefix):
                    return False
        return True


class RuleSum(Rule):
    """Representation of a Rule that checks that the values in given `path` attributes must sum to the given `sum` value.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.
        sum (float): The value that the contents of the located elements and attributes must sum to.

    """

    def __init__(self, context, case):
        """Initialise a `sum` rule."""
        self._name = 'sum'

        super(RuleSum, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleSum is checking."""
        return 'Within each `{self.context}`, the sum of values matched at `{0}` must be `{self.sum}`.'.format('` and `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Assert that the total of the values given in `paths` match the given `sum` value.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when the `path` values total to the `sum` value.
                  Return `False` when the `path` values do not total to the `sum` value.
            None: When no elements are found for the specified `paths`.

        Raises:
            ValueError: When the `path` value is not numeric.

        """
        unique_paths = set(self.paths)
        values_in_context = list()

        for path in unique_paths:
            values_to_sum = self._extract_text_from_element_or_attribute(context_element, path)
            for value in values_to_sum:
                try:
                    values_in_context.append(decimal.Decimal(value))
                except decimal.InvalidOperation:
                    raise ValueError

        if values_in_context == list():
            return None

        if sum(values_in_context) != decimal.Decimal(str(self.sum)):
            return False
        return True


class RuleUnique(Rule):
    """Representation of a Rule that checks that the text of each given path must be unique.

    Attributes:
        paths (list of str): A list of XPath expressions. These are evaluated to locate the elements that the Rule is to operate on.

    """

    def __init__(self, context, case):
        """Initialise a `unique` rule."""
        self._name = 'unique'

        super(RuleUnique, self).__init__(context, case)

    def __str__(self):
        """Return string stating what RuleUnique is checking."""
        return 'Within each `{self.context}`, the text contained within each of the elements and attributes matched by `{0}` must be unique.'.format('` and `'.join(self.paths), **locals())

    def _check_against_Rule(self, context_element):
        """Assert that the given `paths` are not found for `context_element` more than once.

        Args:
            context_element (etree._Element): An XML Element.

        Returns:
            bool: Return `True` when repeated text is not found in the Dataset.
                  Return `False` when repeated text is found in the Dataset.

        Todo:
            Consider better methods for specifying which elements in the tree contain non-permitted duplication, such as bucket sort.

        """
        unique_paths = set(self.paths)
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
