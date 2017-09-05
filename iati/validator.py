"""A module containing validation functionality."""

import sys
from lxml import etree
import yaml
import iati.core.default
import iati.core.resources


class ValidationError(object):
    """A base class to encapsulate information about Validation Errors."""

    def __init__(self, err_name, calling_locals=dict()):
        """Create a new ValidationError.

        Args:
            err_name (str): The name of the error to use as a base.
            calling_locals (dict): The dictionary of local variables from the calling scope. Obtained by calling `locals()`. Default is an empty dictionary.

        Raises:
            ValueError: If there is no base error with the provided name.

        Todo:
            Split message formatting into a child class and raise an error when variables are missing.

        """
        try:
            err_detail = get_error_codes()[err_name]
        except (KeyError, TypeError):
            raise ValueError('{err_name} is not a known type of ValidationError.'.format(**locals()))

        # set general attributes for this type of error
        self.name = err_name

        for key, val in err_detail.items():
            setattr(self, key, val)

        self.status = 'error' if err_name.split('-')[0] =='err' else 'warning'

        # format error messages with context-specific info
        try:
            self.help = self.help.format(**calling_locals)
            self.info = self.info.format(**calling_locals)
        except KeyError as missing_var_err:
            # raise NameError('The calling scope must contain a `{missing_var_err.args[0]}` variable for providing information for the error message.'.format(**locals()))
            pass

        # set general attributes for this type of error that require context from the calling scope
        # TODO: Determine what the defaults should be should the appropriate values not be available
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

    ValidationErrors may be added to the log.

    """

    def __init__(self):
        """Initialise the error log."""
        self._values = []

    def __iter__(self):
        """Return an iterator."""
        return iter(self._values)

    def __len__(self):
        """The number of items in the ErrorLog."""
        return len(self._values)

    def __getitem__(self, key):
        """Return an item with the specified key."""
        return self._values[key]

    def __eq__(self, other):
        """Test equality with another object."""
        if len(self._values) != len(other._values):
            return False

        for val in self._values:
            if not val in other._values:
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
        errors_with_name = [err for err in self._values if err.name == err_name]

        return len(errors_with_name) > 0

    def contains_error_of_type(self, err_type):
        """Check the log for an error or warning with the specified base exception type.

        Args:
            err_type (type): The type of the error to look for.

        Returns:
            bool: Whether there is an error or warning with the specified type within the log.

        """
        errors_with_type = [err for err in self._values if err.base_exception == err_type]

        return len(errors_with_type) > 0


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

    def contains_errors(self):
        """Determine whether there are errors contained within the ErrorLog.

        Note:
            The error log may contain warnings, or may be empty.

        Returns:
            bool: Whether there are errors within this error log.

        """
        actual_errors = [err for err in self if err.status == 'error']

        return len(actual_errors) > 0

    def contains_warnings(self):
        """Determine whether there are warnings contained within the ErrorLog.

        Note:
            The error log may contain errors, or may be empty.

        Returns:
            bool: Whether there are warnings within this error log.

        """
        actual_warnings = [err for err in self if err.status == 'warning']

        return len(actual_warnings) > 0


def _check_codes(dataset, codelist):
    """Determine whether a given Dataset has values from the specified Codelist where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        codelist (iati.core.codelists.Codelist): The Codelist to check values from.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    """
    error_log = ValidationErrorLog()
    mappings = iati.core.default.codelist_mapping()

    for mapping in mappings[codelist.name]:
        base_xpath = mapping['xpath']
        condition = mapping['condition']
        split_xpath = base_xpath.split('/')
        parent_el_xpath = '/'.join(split_xpath[:-1])
        attr_name = split_xpath[-1:][0][1:]

        if condition is None:
            parent_el_xpath = parent_el_xpath + '[@' + attr_name + ']'
        else:
            parent_el_xpath = parent_el_xpath + '[' + condition + ' and @' + attr_name + ']'

        parents_to_check = dataset.xml_tree.xpath(parent_el_xpath)

        for parent in parents_to_check:
            code = parent.attrib[attr_name]

            if code not in codelist.codes:
                line_number = parent.sourceline

                if codelist.complete:
                    error = ValidationError('err-code-not-on-codelist', locals())
                else:
                    error = ValidationError('warn-code-not-on-codelist', locals())

                error.actual_value = code

                error_log.add(error)

    return error_log


def _check_codelist_values(dataset, schema):
    """Check whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.core.schemas.Schema): The Schema to locate Codelists within.

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
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.

    Raises:
        iati.core.exceptions.SchemaError: An error occurred in the parsing of the Schema.

    Todo:
        Create test against a bad Schema.

    """
    error_log = ValidationErrorLog()

    try:
        validator = schema.validator()
    except iati.core.exceptions.SchemaError as err:
        raise err

    try:
        validator.assertValid(dataset.xml_tree)
    except etree.DocumentInvalid as doc_invalid:
        for log_entry in doc_invalid.error_log:
            error = _parse_lxml_log_entry(log_entry)
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

    if isinstance(maybe_xml, iati.core.data.Dataset):
        maybe_xml = maybe_xml.xml_str

    try:
        parser = etree.XMLParser()
        _ = etree.fromstring(maybe_xml.strip(), parser)
    except etree.XMLSyntaxError:
        for log_entry in parser.error_log:
            error = _parse_lxml_log_entry(log_entry)
            error_log.add(error)
    except (AttributeError, TypeError, ValueError):
        problem_var_type = type(maybe_xml)
        error = ValidationError('err-not-xml-not-string', locals())
        error_log.add(error)

    # the parser does not cause any errors when given an empty string, so this needs handling separately
    if len(error_log) == 0 and len(maybe_xml.strip()) == 0:
        err_name = 'err-not-xml-empty-document'
        err = 'A file or string containing no data is not XML.'
        error = ValidationError(err_name, locals())
        error_log.add(error)

    return error_log


def _correct_codelist_values(dataset, schema):
    """Determine whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.core.schemas.Schema): The Schema to locate Codelists within.

    Returns:
        bool: If `error_log` is False. A boolean indicating whether the given Dataset has values from the specified Codelists where they should be.

    """
    error_log = _check_codelist_values(dataset, schema)

    return not error_log.contains_errors()


def _parse_lxml_log_entry(log_entry):
    """Parse a log entry from an lxml error log and convert it to a IATI ValidationError.

    Args:
        log_entry (etree._LogEntry): A log entry from an `etree.XMLSyntaxError` or `etree.DocumentInvalid`.

    Returns:
        ValidationError: An IATI ValidationError that contains the information from the log entry.

    Todo:
        Create a small program to determine the common types of errors so that they can be handled as special cases with detailed help info.

    """
    # set the `err` variable so it can be used in error string formatting via locals()
    err = log_entry

    # configure local variables for the creation of the error
    line_number = err.line
    column_number = err.column

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
        # TODO: it may be desired to make there be different uncategorised errors - eg. IATI error vs. XML error
        err_name = 'err-not-xml-uncategorised-xml-syntax-error'

    error = ValidationError(err_name, locals())

    return error


def full_validation(dataset, schema):
    """Perform full validation on a Dataset.

    Args:
        dataset (iati.core.Dataset): The Dataset to check validity of.
        schema (iati.core.Schema): The Schema to validate the Dataset against.

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
    err_codes_str = iati.core.resources.load_as_string(iati.core.resources.get_lib_data_path('validation_err_codes.yaml'))
    err_codes_list_of_dict = yaml.safe_load(err_codes_str)
    # yaml parses the values into a list of dicts, so they need combining into one
    err_codes_dict = { k: v for code in err_codes_list_of_dict for k, v in code.items() }

    # convert name of exception into reference to the relevant class
    for _, err in err_codes_dict.items():
        # python2/3 have exceptions in different modules, though six and future do not appear to have a standard workaround for this
        try:
            err['base_exception'] = getattr(sys.modules['builtins'], err['base_exception'])
        except KeyError:
            err['base_exception'] = getattr(sys.modules['exceptions'], err['base_exception'])

    return err_codes_dict


def is_iati_xml(dataset, schema):
    """Determine whether a given Dataset's XML is valid against the specified Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML against the given Schema.

    Raises:
        iati.core.exceptions.SchemaError: An error occurred in the parsing of the Schema.

    Todo:
        Create test against a bad Schema.

    """
    return not _check_is_iati_xml(dataset, schema).contains_errors()


def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.core.Dataset): The Dataset to check validity of.
        schema (iati.core.Schema): The Schema to validate the Dataset against.

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
    except iati.core.exceptions.SchemaError:
        return False

    return _correct_codelist_values(dataset, schema)


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
         dataset (iati.core.Dataset): The Dataset to check validity of.

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
