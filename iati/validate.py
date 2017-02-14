"""A module containing validation functionality."""
import iati.core.data
import iati.core.schemas

def is_valid(dataset, schema):
    """Determine whether a given Dataset is valid against the specified Schema.

    Args:
        dataset (iati.core.data.Dataset): The Dataset to check validity of.
        schema (iati.core.schemas.Schema): The Schema to validate the Dataset against.

    Todo:
        Auto-detect Schema version.
    """
    pass
