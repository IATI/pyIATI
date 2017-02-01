"""A module containing IATI exceptions."""


class SchemaError(Exception):
    """An error with an IATI Schema."""

    pass


class ValidationError(ValueError):
    """An error with XML.

    Indicates that the XML does not conform to the IATI standard.
    """

    pass
