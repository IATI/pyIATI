"""A module containing validation functionality."""

from lxml import etree
import iati.core.default


class ErrorLog(set):
    pass


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
    }
}


def _base_error(err_name, calling_locals):
    """Create the base error with a particular name.

    Args:
        err_name (str): The name of the error to obtain basic information for.
        calling_locals (dict): The dictionary of local variables from the calling scope. Obtained by calling `locals()`.

    Returns:
        dict: A populated base error.

    Raises:
        ValueError: If the `err_name` is not a valid name for an error.

    """
    try:
        base_err = _ERROR_CODES[err_name]
    except KeyError:
        raise ValueError

    base_err['name'] = err_name
    # format error messages with context-specific info
    base_err['help'] = base_err['help'].format(**calling_locals)
    base_err['info'] = base_err['info'].format(**calling_locals)

    base_err['status'] = 'error' if err_name.split('-')[0] =='err' else 'warning'

    # obtain additional information
    base_err['line_number'] = calling_locals['line_number']
    base_err['context'] = calling_locals['dataset'].source_around_line(base_err['line_number'])

    return base_err


def _correct_codes(dataset, codelist, error_log=False):
    """Determine whether a given Dataset has values from the specified Codelist where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        codelist (iati.core.codelists.Codelist): The Codelist to check values from.
        error_log (bool): Whether to return a detailed error log, or merely a boolean value. Default False.

    Returns:
        bool: If `error_log` is False. A boolean indicating whether the given Dataset has values from the specified Codelist where they should be.
        list of dict: If `error_log` is True. A list of the errors that occurred.

    """
    errors = []
    mappings = iati.core.default.codelist_mapping()

    if not error_log and not codelist.complete:
        return True

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
                if error_log:
                    line_number = parent.sourceline
                    if codelist.complete:
                        error = _base_error('err-code-not-on-codelist', locals())
                    else:
                        error = _base_error('warn-code-not-on-codelist', locals())

                    error['actual_value'] = code

                    errors.append(error)
                else:
                    return False

    if error_log:
        return errors
    else:
        return True


def _correct_codelist_values(dataset, schema, error_log=False):
    """Determine whether a given Dataset has values from Codelists that have been added to a Schema where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        schema (iati.core.schemas.Schema): The Schema to locate Codelists within.
        error_log (bool): Whether to return a detailed error log, or merely a boolean value. Default False.

    Returns:
        bool: If `error_log` is False. A boolean indicating whether the given Dataset has values from the specified Codelists where they should be.
        list of dict: If `error_log` is True. A list of the errors that occurred.

    """
    errors = []

    for codelist in schema.codelists:
        if error_log:
            errors = errors + _correct_codes(dataset, codelist, error_log)
        else:
            correct_for_codelist = _correct_codes(dataset, codelist)
            if not correct_for_codelist:
                return False

    if error_log:
        return errors
    else:
        return True


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
    return _correct_codelist_values(dataset, schema, True)


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
    if isinstance(maybe_xml, iati.core.data.Dataset):
        maybe_xml = maybe_xml.xml_str

    try:
        _ = etree.fromstring(maybe_xml.strip())
        return True
    except (etree.XMLSyntaxError, AttributeError, TypeError, ValueError):
        return False

