"""A module containing validation functionality."""

import sys
from lxml import etree
import yaml
import iati.default
import iati.resources


class ValidationError(object):
    """A base class to encapsulate information about Validation Errors."""

    # pylint: disable=too-many-instance-attributes
    def __init__(self, err_name, calling_locals=None):
        """Create a new ValidationError.

        Args:
            err_name (str): The name of the error to use as a base.
            calling_locals (dict): The dictionary of local variables from the calling scope. Obtained by calling `locals()`. Default is an empty dictionary.

        Raises:
            ValueError: If there is no base error with the provided name.

        Todo:
            Split message formatting into a child class and raise an error when variables are missing.

            Determine what defaults for attributes should be when the appropriate values are not available.

        """
        # have to set here to ensure each ValidationError has its own dictionary
        if calling_locals is None:
            calling_locals = dict()

        try:
            err_detail = get_error_codes()[err_name]
        except (KeyError, TypeError):
            raise ValueError('{err_name} is not a known type of ValidationError.'.format(**locals()))

        # set general attributes for this type of error
        self.name = err_name
        self.actual_value = None

        for key, val in err_detail.items():
            setattr(self, key, val)

        self.status = 'error' if err_name.split('-')[0] == 'err' else 'warning'

        # format error messages with context-specific info
        try:
            self.help = self.help.format(**calling_locals)
            self.info = self.info.format(**calling_locals)
        except KeyError:  # as missing_var_err:
            # raise NameError('The calling scope must contain a `{missing_var_err.args[0]}` variable for providing information for the error message.'.format(**locals()))
            pass

        # set general attributes for this type of error that require context from the calling scope
        try:
            self.line_number = calling_locals['line_number']
            self.context = calling_locals['dataset'].source_around_line(self.line_number)
        except KeyError:
            pass
        try:
            self.column_number = calling_locals['column_number']
        except KeyError:
            pass
        try:
            self.err = calling_locals['err']
            self.lxml_err_code = calling_locals['err'].type_name
        except (AttributeError, KeyError):
            pass


class ValidationErrorLog(object):
    """A container to keep track of a set of ValidationErrors.

    This acts as an iterable that ValidationErrors can be looped over.

    ValidationErrors may be added to the log.

    Warning:
        It is highly likely that the methods available on a `ValidationErrorLog` will change name. At present the mix of errors, warnings and the combination of the two is confusing. This needs rectifying.

    Todo:
        Make the mix of errors, warnings and both returned by functions clearer, while not being hugely long-winded (`errors_and_warnings`-esque).

    """

    def __init__(self):
        """Initialise the error log."""
        self._values = []

    def __iter__(self):
        """Return an iterator."""
        return iter(self._values)

    def __len__(self):
        """Return the number of items in the ErrorLog."""
        return len(self._values)

    def __getitem__(self, key):
        """Return an item with the specified key."""
        return self._values[key]

    def __eq__(self, other):
        """Test equality with another object."""
        if len(self._values) != len(other):
            return False

        for val in self._values:
            if val not in other:
                return False

        return True

    def add(self, value):
        """Add a single ValidationError to the Error Log.

        Args:
            value (iati.validator.ValidationError): The ValidationError to add to the Error Log.

        Raises:
            TypeError: When attempting to set an item that is not a ValidationError.

        """
        if not isinstance(value, iati.validator.ValidationError):
            raise TypeError('Only ValidationErrors may be added to a ValidationErrorLog.')

        self._values.append(value)

    def contains_error_called(self, err_name):
        """Check the log for an error or warning with the specified name.

        Args:
            err_name (str): The name of the error to look for.

        Returns:
            bool: Whether there is an error or warning with the specified name within the log.

        """
        errors_with_name = self.get_errors_or_warnings_by_name(err_name)

        return len(errors_with_name) > 0

    def contains_error_of_type(self, err_type):
        """Check the log for an error or warning with the specified base exception type.

        Args:
            err_type (type): The type of the error to look for.

        Returns:
            bool: Whether there is an error or warning with the specified type within the log.

        """
        errors_with_type = self.get_errors_or_warning_by_type(err_type)

        return len(errors_with_type) > 0

    def contains_errors(self):
        """Determine whether there are errors contained within the ErrorLog.

        Note:
            The error log may contain warnings, or may be empty.

        Returns:
            bool: Whether there are errors within this error log.

        """
        errors = self.get_errors()

        return len(errors) > 0

    def contains_warnings(self):
        """Determine whether there are warnings contained within the ErrorLog.

        Note:
            The error log may contain errors, or may be empty.

        Returns:
            bool: Whether there are warnings within this error log.

        """
        warnings = self.get_warnings()

        return len(warnings) > 0

    def extend(self, values):
        """Extend the ErrorLog with ValidationErrors from an iterable.

        Args:
            values (iterable): An iterable containing ValidationErrors.

        Note:
            All ValidationErrors within the iterable shall be added. Any other contents shall not, and will fail to be added silently.

        Raises:
            TypeError: When values is not an iterable.

        """
        for value in values:
            try:
                self.add(value)
            except TypeError:
                pass

    def get_errors(self):
        """Return a list of errors contained.

        Returns:
            list(ValidationError): A list of all errors (but not warnings) that are present within the log.

        Todo:
            Add explicit tests.

        """
        return [err for err in self if err.status == 'error']

    def get_errors_or_warnings_by_category(self, err_category):
        """Return a list of errors or warnings of the specified category.

        Args:
            err_category (str): The category of the error to look for.

        Returns:
            list(ValidationError): A list of errors and warnings of the specified category that are present within the log.

        Todo:
            Add explicit tests.

        """
        return [err for err in self._values if err.category == err_category]

    def get_errors_or_warnings_by_name(self, err_name):
        """Return a list of errors or warnings with the specified name.

        Args:
            err_name (str): The name of the error to look for.

        Returns:
            list(ValidationError): A list of errors and warnings with the specified name that are present within the log.

        Todo:
            Add explicit tests.

        """
        return [err for err in self._values if err.name == err_name]

    def get_errors_or_warning_by_type(self, err_type):
        """Return a list of errors or warnings of the specified type.

        Args:
            err_type (type): The type of the error to look for.

        Returns:
            list(ValidationError): A list of errors and warnings of the specified type that are present within the log.

        Todo:
            Add explicit tests.

        """
        return [err for err in self._values if err.base_exception == err_type]

    def get_warnings(self):
        """Return a list of warnings contained.

        Returns:
            list(ValidationError): A list of all warnings (but not errors) that are present within the log.

        Todo:
            Add explicit tests.

        """
        return [err for err in self if err.status == 'warning']


def _extract_codes_from_attrib(dataset, parent_el_xpath, attr_name, condition=None):
    """Extract codes for checking from a Dataset. The codes are being extracted from attributes.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        parent_el_xpath (str): An XPath to locate the element(s) with the attribute of interest.
        attr_name (str): The name of the attribute to extract a code from.
        condition (str): An optional XPath expression to limit the scope of what is extracted.

    Returns:
        list of tuple: A tuple in the format: `(str, int)` - The `str` is a matching code from within the Dataset; The `int` is the sourceline at which the parent element is located.

    """
    if condition is None:
        parent_el_xpath = parent_el_xpath + '[@' + attr_name + ']'
    else:
        parent_el_xpath = parent_el_xpath + '[' + condition + ' and @' + attr_name + ']'

    # some nasty string manipulation to make the `//@xml:lang` mapping work
    while not parent_el_xpath.startswith('//'):
        parent_el_xpath = '/' + parent_el_xpath
    if parent_el_xpath.startswith('//['):
        parent_el_xpath = '//*[' + parent_el_xpath[3:]
    # provide a secondary cludge to deal with the 'xml' namespace
    if attr_name == 'xml:lang':
        attr_name = '{http://www.w3.org/XML/1998/namespace}lang'

    parents_to_check = dataset.xml_tree.xpath(parent_el_xpath)

    located_codes = list()
    for parent in parents_to_check:
        located_codes.append((parent.attrib[attr_name], parent.sourceline))

    return located_codes


def _extract_codes_from_element_text(dataset, parent_el_xpath, condition=None):  # pylint: disable=invalid-name
    """Extract codes for checking from a Dataset. The codes are being extracted from element text.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        parent_el_xpath (str): An XPath to locate the element(s) with the attribute of interest.
        condition (str): An optional XPath expression to limit the scope of what is extracted.

    Returns:
        list of tuple: A tuple in the format: `(str, int)` - The `str` is a matching code from within the Dataset; The `int` is the sourceline at which the parent element is located.

    """
    # include the condition
    if condition:
        parent_el_xpath = parent_el_xpath + '[' + condition + ']'

    parents_to_check = dataset.xml_tree.xpath(parent_el_xpath)

    located_codes = list()
    for parent in parents_to_check:
        located_codes.append((parent.text, parent.sourceline))

    return located_codes


def _extract_codes(dataset, parent_el_xpath, last_xpath_section, condition=None):
    """Extract codes for checking from a Dataset.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        parent_el_xpath (str): An XPath to locate the element(s) with the code of interest.
        last_xpath_section (str): The last section of the XPath, detailing how to find the code on the identified element(s).
        condition (str): An optional XPath expression to limit the scope of what is extracted.

    list of tuple: A tuple in the format: `(str, int)` - The `str` is a matching code from within the Dataset; The `int` is the sourceline at which the parent element is located.

    Raises:
        ValueError: When a path in a mapping is not looking for an attribute value or element text.

    """
    if last_xpath_section.startswith('@'):
        attr_name = last_xpath_section[1:]
        return _extract_codes_from_attrib(dataset, parent_el_xpath, attr_name, condition)
    elif last_xpath_section == 'text()':
        return _extract_codes_from_element_text(dataset, parent_el_xpath, condition)
    else:
        raise ValueError('mapping path does not locate attribute value or element text')


def _check_codes(dataset, codelist):
    """Determine whether a given Dataset has values from the specified Codelist where expected.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        codelist (iati.codelists.Codelist): The Codelist to check values from.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    Raises:
        ValueError: When a path in a mapping is looking for a type of information that is not supported.

    Todo:
        Stop this being fixed to 2.02.

    """
    error_log = ValidationErrorLog()

    # clunky workaround due to pre-#230 behavior of `iati.Dataset().version`
    if dataset.version in iati.constants.STANDARD_VERSIONS:
        mappings = iati.default.codelist_mapping(dataset.version)
    else:
        # rather than attempting general checks, ensure version number errors occur
        codelist = iati.default.codelist('Version', '2.02')
        mappings = iati.default.codelist_mapping('2.02')

    err_name_prefix = 'err' if codelist.complete else 'warn'

    for mapping in mappings[codelist.name]:
        parent_el_xpath, last_xpath_section = mapping['xpath'].rsplit('/', 1)

        located_codes = _extract_codes(dataset, parent_el_xpath, last_xpath_section, mapping['condition'])

        for (code, line_number) in located_codes:  # `line_number` used via `locals()` # pylint: disable=unused-variable
            if code not in codelist.codes:
                if last_xpath_section.startswith('@'):
                    attr_name = last_xpath_section[1:]  # used via `locals()`  # pylint: disable=unused-variable
                    error = ValidationError(err_name_prefix + '-code-not-on-codelist', locals())
                else:
                    _, el_name = parent_el_xpath.rsplit('/', 1)  # used via `locals()` # pylint: disable=unused-variable
                    error = ValidationError(err_name_prefix + '-code-not-on-codelist-element-text', locals())

                error.actual_value = code

                error_log.add(error)

    return error_log


def _check_codelist_values(dataset, schema):
    """Check whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.schemas.Schema): The Schema to locate Codelists within.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    error_log = ValidationErrorLog()

    for codelist in schema.codelists:
        error_log.extend(_check_codes(dataset, codelist))

    return error_log


def _check_is_iati_xml(dataset, schema):
    """Check whether a given Dataset contains valid IATI XML.

    Args:
        dataset (iati.data.Dataset): The Dataset to check validity of.
        schema (iati.schemas.Schema): The Schema to validate the Dataset against.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    Raises:
        iati.exceptions.SchemaError: An error occurred in the parsing of the Schema.

    Todo:
        Create test against a bad Schema.

    """
    error_log = ValidationErrorLog()

    try:
        validator = schema.validator()
    except iati.exceptions.SchemaError as err:
        raise err

    try:
        validator.assertValid(dataset.xml_tree)
    except etree.DocumentInvalid as doc_invalid:
        for log_entry in doc_invalid.error_log:  # pylint: disable=no-member
            error = _create_error_for_lxml_log_entry(log_entry)
            error_log.add(error)

    return error_log


def _check_is_xml(maybe_xml):
    """Check whether a given parameter is valid XML.

    Args:
        maybe_xml (str): An string that may or may not contain valid XML.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    Todo:
        Consider how a Dataset may be passed when creating errors so that context can be obtained.

    """
    error_log = ValidationErrorLog()

    if isinstance(maybe_xml, iati.data.Dataset):
        maybe_xml = maybe_xml.xml_str

    try:
        parser = etree.XMLParser()
        _ = etree.fromstring(maybe_xml.strip(), parser)
    except etree.XMLSyntaxError:
        for log_entry in parser.error_log:
            error = _create_error_for_lxml_log_entry(log_entry)
            error_log.add(error)
    except (AttributeError, TypeError, ValueError):
        problem_var_type = type(maybe_xml)  # used via `locals()` # pylint: disable=unused-variable
        error = ValidationError('err-not-xml-not-string', locals())
        error_log.add(error)

    # the parser does not cause any errors when given an empty string, so this needs handling separately
    if error_log == ValidationErrorLog() and maybe_xml.strip() == '':
        err_name = 'err-not-xml-empty-document'
        err = 'A file or string containing no data is not XML.'  # used via `locals()` # pylint: disable=unused-variable
        error = ValidationError(err_name, locals())
        error_log.add(error)

    return error_log


def _check_rules(dataset, ruleset):
    """Determine whether a given Dataset conforms with a provided Ruleset.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Ruleset conformance with.
        ruleset (iati.code.Ruleset): The Ruleset to check conformance with.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    error_log = ValidationErrorLog()
    error_found = False

    for rule in ruleset.rules:
        validation_status = rule.is_valid_for(dataset)
        if validation_status is None:
            # A result of `None` signifies that a rule was skipped.
            error = ValidationError('warn-rule-skipped', locals())
            error_log.add(error)
        elif validation_status is False:
            # A result of `False` signifies that a rule did not pass.
            error = _create_error_for_rule(rule)
            error_log.add(error)
            error_found = True

    if error_found:
        # Add a ruleset error if at least one rule error was found.
        error = ValidationError('err-ruleset-conformance-fail', locals())
        error_log.add(error)

    return error_log


def _check_ruleset_conformance(dataset, schema):
    """Check whether a given Dataset conforms with Rulesets that have been added to a Schema.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Ruleset conformance with.
        schema (iati.schemas.Schema): The Schema to locate Rulesets within.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    error_log = ValidationErrorLog()

    for ruleset in schema.rulesets:
        error_log.extend(_check_rules(dataset, ruleset))

    return error_log


def _conforms_with_ruleset(dataset, schema):
    """Determine whether a given Dataset conforms with Rulesets that have been added to a Schema.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Ruleset conformance with.
        schema (iati.schemas.Schema): The Schema to locate Rulesets within.

    Returns:
        bool: A boolean indicating whether the given Dataset conforms with Rulesets attached to the given Schema.

    """
    error_log = _check_ruleset_conformance(dataset, schema)

    return not error_log.contains_errors()


def _correct_codelist_values(dataset, schema):
    """Determine whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.schemas.Schema): The Schema to locate Codelists within.

    Returns:
        bool: A boolean indicating whether the given Dataset has values from the specified Codelists where they should be.

    """
    error_log = _check_codelist_values(dataset, schema)

    return not error_log.contains_errors()


def _create_error_for_lxml_log_entry(log_entry):  # pylint: disable=invalid-name
    """Parse a log entry from an lxml error log and convert it to a IATI ValidationError.

    Args:
        log_entry (etree._LogEntry): A log entry from an `etree.XMLSyntaxError` or `etree.DocumentInvalid`.

    Returns:
        ValidationError: An IATI ValidationError that contains the information from the log entry.

    Todo:
        Create a small program to determine the common types of errors so that they can be handled as special cases with detailed help info.

        Determine whether there should be a range of uncategorised errors rather than just 'err-not-xml-uncategorised-xml-syntax-error' eg. IATI error vs. XML error.

    """
    # set the `err` variable so it can be used in error string formatting via locals()
    err = log_entry

    # configure local variables for the creation of the error
    line_number = err.line  # used via `locals()`# pylint: disable=unused-variable
    column_number = err.column  # used via `locals()`# pylint: disable=unused-variable

    # undertake the mapping between error name formats
    lxml_to_iati_error_mapping = {
        'ERR_DOCUMENT_EMPTY': 'err-not-xml-empty-document',
        'ERR_DOCUMENT_END': 'err-not-xml-content-at-end',
        'ERR_INTERNAL_ERROR': 'err-lxml-internal-error',
        'ERR_INVALID_ENCODING': 'err-encoding-invalid',
        'ERR_UNSUPPORTED_ENCODING': 'err-encoding-unsupported',
        'ERR_RESERVED_XML_NAME': 'err-not-xml-xml-text-decl-only-at-doc-start',
        'SCHEMAV_CVC_COMPLEX_TYPE_2_3': 'err-not-iati-xml-non-whitespace-in-element-only',
        'SCHEMAV_CVC_COMPLEX_TYPE_3_2_1': 'err-not-iati-xml-forbidden-attribute',
        'SCHEMAV_CVC_COMPLEX_TYPE_3_2_2': 'err-not-iati-xml-forbidden-attribute',
        'SCHEMAV_CVC_COMPLEX_TYPE_4': 'err-not-iati-xml-missing-attribute',
        'SCHEMAV_CVC_DATATYPE_VALID_1_2_1': 'err-not-iati-xml-incorrect-datatype',
        'SCHEMAV_CVC_ELT_1': 'err-not-iati-xml-root-element-undeclared',
        'SCHEMAV_ELEMENT_CONTENT': 'err-not-iati-xml-missing-required-element'
    }

    try:
        err_name = lxml_to_iati_error_mapping[err.type_name]
    except KeyError:
        err_name = 'err-not-xml-uncategorised-xml-syntax-error'

    error = ValidationError(err_name, locals())

    return error


def _create_error_for_rule(rule):
    """Parse a Rule skip or failure and convert it into an IATI ValidationError.

    Args:
        rule (iati.rulesets.Rule): The Rule which has either skipped or failed.

    Returns:
        ValidationError: An IATI ValidationError that contains information about the Rule that has failed.

    Todo:
        Determine whether there should be a range of uncategorised errors for various ways Ruleset validation may fail, rather than just 'err-rule-uncategorised-conformance-fail'.

    """
    # undertake the mapping between Rule subclass and error name formats
    rule_to_iati_error_mapping = {
        'atleast_one': 'err-rule-at-least-one-conformance-fail',
        'date_order': 'err-rule-date-order-conformance-fail',
        'dependent': 'err-rule-dependent-conformance-fail',
        'no_more_than_one': 'err-rule-no-more-than-one-conformance-fail',
        'regex_matches': 'err-rule-regex-matches-conformance-fail',
        'regex_no_matches': 'err-rule-regex-no-matches-conformance-fail',
        'startswith': 'err-rule-starts-with-conformance-fail',
        'sum': 'err-rule-sum-conformance-fail',
        'unique': 'err-rule-unique-conformance-fail'
    }

    try:
        err_name = rule_to_iati_error_mapping[rule.name]
    except KeyError:
        err_name = 'err-rule-uncategorised-conformance-fail'

    error = ValidationError(err_name, locals())

    return error


def full_validation(dataset, schema):
    """Perform full validation on a Dataset.

    Args:
        dataset (iati.Dataset): The Dataset to check validity of.
        schema (iati.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    Todo:
        Create test against a bad Schema.

    """
    error_log = ValidationErrorLog()

    error_log.extend(_check_is_xml(dataset))
    error_log.extend(_check_codelist_values(dataset, schema))
    error_log.extend(_check_ruleset_conformance(dataset, schema))

    return error_log


def get_error_codes():
    """Return a dictionary of the possible error codes and their information.

    Returns:
        dict: A dictionary of error codes.

    Raises:
        KeyError: When a specified base_exception is not a valid type of exception.

    Todo:
        Raise the correct error for incorrect base_exception values.
        Raise an error when there is a problem with non-base_exception-related errors.

    """
    err_codes_str = iati.resources.load_as_string(iati.resources.get_lib_data_path('validation_err_codes.yaml'))
    err_codes_list_of_dict = yaml.safe_load(err_codes_str)
    # yaml parses the values into a list of dicts, so they need combining into one
    err_codes_dict = {k: v for code in err_codes_list_of_dict for k, v in code.items()}

    # convert name of exception into reference to the relevant class
    for err in err_codes_dict.values():
        # python2/3 have exceptions in different modules, though six and future do not appear to have a standard workaround for this
        try:
            err['base_exception'] = getattr(sys.modules['builtins'], err['base_exception'])
        except KeyError:
            err['base_exception'] = getattr(sys.modules['exceptions'], err['base_exception'])

    return err_codes_dict


def is_iati_xml(dataset, schema):
    """Determine whether a given Dataset's XML is valid against the specified Schema.

    Args:
        dataset (iati.data.Dataset): The Dataset to check validity of.
        schema (iati.schemas.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML against the given Schema.

    Raises:
        iati.exceptions.SchemaError: An error occurred in the parsing of the Schema.

    Todo:
        Create test against a bad Schema.

    """
    return not _check_is_iati_xml(dataset, schema).contains_errors()


def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.Dataset): The Dataset to check validity of.
        schema (iati.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid against the given Schema.

    Todo:
        Create test against a bad Schema.

    """
    try:
        iati_xml = is_iati_xml(dataset, schema)
        if not iati_xml:
            return False
    except iati.exceptions.SchemaError:
        return False

    correct_codelist_values = _correct_codelist_values(dataset, schema)
    conforms_with_ruleset = _conforms_with_ruleset(dataset, schema)

    return correct_codelist_values and conforms_with_ruleset


def is_xml(maybe_xml):
    """Determine whether a given parameter is XML.

    Args:
        maybe_xml (str): An string that may or may not be valid XML.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML.

    """
    error_log = _check_is_xml(maybe_xml)

    return not error_log.contains_errors()


def validate_is_iati_xml(dataset, schema):
    """Check whether a Dataset contains valid IATI XML.

    Args:
        dataset (iati.Dataset): The Dataset to check validity of.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    return _check_is_iati_xml(dataset, schema)


def validate_is_xml(maybe_xml):
    """Check whether a Dataset contains valid XML.

    Args:
        maybe_xml (str): An string that may or may not be valid XML.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    return _check_is_xml(maybe_xml)
