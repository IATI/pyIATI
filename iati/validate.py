"""A module containing validation functionality.

Warning:
    It is planned to change from Schema-based to Data-based Codelist validation. As such, this module will change significantly.
"""

from lxml import etree
import iati.core.default


def _correct_codelist_values(dataset, codelist_name):
    """Determine whether a given Dataset has values from the specified Codelist where expected.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check Codelist values within.
        codelist_name (str): The name of the Codelist to check values from.

    Returns:
        bool: A boolean indicating whether the given Dataset has values from the specified Codelist where they should be.

    Todo:
        Test invalid Codelist name.
        Test something with a condition

    """
    mappings = iati.core.default.codelist_mapping()
    codelist = iati.core.default.codelist(codelist_name)
    xpath = mappings[codelist_name]['xpath']
    codes_to_check = [iati.core.codelists.Code(value) for value in dataset.xml_tree.xpath(xpath)]

    for code_to_check in codes_to_check:
        if code_to_check not in codelist.codes:
            return False

    return True


def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.

    Returns:
        bool: A boolean indicating whether the given Dataset is valid against the given Schema.

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
        return _correct_codelist_values(dataset, 'Version')
    except etree.DocumentInvalid as exception_obj:
        return False
