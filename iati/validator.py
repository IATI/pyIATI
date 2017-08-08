"""A module containing validation functionality."""

from lxml import etree
import iati.core.default


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
            err_detail = _ERROR_CODES[err_name]
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
        try:
            self.line_number = calling_locals['line_number']
            self.context = calling_locals['dataset'].source_around_line(self.line_number)
        except KeyError:
            # TODO: Determine what the defaults should be should the appropriate values not be available
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


    def extend(self, values):
        """Extend the ErrorLog with ValidationErrors from an iterable.

        Args:
            values (iterable): An iterable containing ValidationErrors.

        Note:
            All ValidationErrors within the iterable shall be added. Any other contents shall not, and will fail to be added silently.

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



_ERROR_CODES = {
    'err-code-not-on-codelist': {
        'category': 'codelist',
        'description': 'An attribute that requires a Code from a particular complete Codelist contained a value not on the Codelist.',
        'info': '{code} is not a valid Code on the {codelist.name} Codelist.',
        'help': 'The `{attr_name}` attribute must contain a value on the `{codelist.name}` Codelist.\nSee http://iatistandard.org/202/codelists/{codelist.name} for permitted values.'
    },
    'warn-code-not-on-codelist': {
        'category': 'codelist',
        'description': 'An attribute that should contain a Code from a particular incomplete Codelist contained a value not on the Codelist.',
        'info': '{code} is not a Code on the {codelist.name} Codelist. ',
        'help': 'The `{attr_name}` attribute should contain a value on the `{codelist.name}` Codelist. Note that values not on the Codelist may be valid in particular circumstances.\nSee http://iatistandard.org/202/codelists/{codelist.name} for values on the Codelist.'
    },
    'err-not-xml-not-string': {
        'category': 'xml',
        'description': 'A variable that is not a string cannot be XML.',
        'info': 'The value provided is a `{problem_var_type}` rather than a `str`.',
        'help': 'A string is a series of characters (letters, numbers, punctuation, etc). For more information about what these are, see https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str'
    }
}


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


def _check_is_xml(maybe_xml):
    """Check whether a given parameter is valid XML.

    Args:
        maybe_xml (str): An string that may or may not contain valid XML.

    Returns:
        iati.validator.ValidationErrorLog: A log of the errors that occurred.
    """
    error_log = ValidationErrorLog()

    if isinstance(maybe_xml, iati.core.data.Dataset):
        maybe_xml = maybe_xml.xml_str

    try:
        _ = etree.fromstring(maybe_xml.strip())
        return True
    except etree.XMLSyntaxError as err:
        return False
    except (AttributeError, TypeError, ValueError):
        problem_var_type = type(maybe_xml)
        error = ValidationError('err-not-xml-not-string', locals())
        error_log.add(error)
    except ValueError as err:
        return False

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


def full_validation(dataset, schema):
    """Perform full validation on a Dataset.

    Args:
        dataset (iati.core.Dataset): The Dataset to check validity of.
        schema (iati.core.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        list of dict: A list of dictionaries containing error output. An empty list indicates that there are no errors.

    Todo:
        Create test against a bad Schema.

    """
    return _check_codelist_values(dataset, schema)


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
    try:
        validator = schema.validator()
    except iati.core.exceptions.SchemaError as err:
        raise err

    try:
        validator.assertValid(dataset.xml_tree)
    except etree.DocumentInvalid:
        return False

    return True


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
        maybe_xml (str): An string that may or may not contain valid XML.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid XML.

    """
    error_log = _check_is_xml(maybe_xml)

    if isinstance(error_log, ValidationErrorLog):
        return not error_log.contains_errors()
    else:
        return error_log

