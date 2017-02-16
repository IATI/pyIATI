"""A module containing IATI exceptions."""
from lxml import etree


class SchemaError(Exception):
    """An error with an IATI Schema."""

    pass


class ValidationError(ValueError):
    """An error with XML.

    Indicates that the XML does not conform to the IATI standard.
    """

    pass
