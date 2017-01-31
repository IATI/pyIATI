"""A module containing utility functions."""
from lxml import etree


def convert_to_schema(tree):
    """Convert an etree to a schema.

    This additionally involves checking that imported schemas also work.
    """
    # TODO: surround schema conversion with error handling
    return etree.XMLSchema(tree)
