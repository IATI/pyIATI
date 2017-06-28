"""A module containing validation functionality.

Warning:
    It is planned to change from Schema-based to Data-based Codelist validation. As such, this module will change significantly.
"""

from lxml import etree


def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Warning:
        Parameters are likely to change in some manner.
    """
    try:
        validator = schema.validator(dataset)
        if validator is not False:
            validator.assertValid(dataset.xml_tree)
        return True
    except etree.DocumentInvalid:
        return False
