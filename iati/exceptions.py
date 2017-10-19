"""A module containing IATI exceptions.

Warning:
    Proper thought needs to be put into error handling. The currently defined errors do not handle existing use-cases, let alone those that may exist in the future.
"""


class SchemaError(Exception):
    """An error with an IATI Schema.

    Warning:
        Highly likely to change.

        Should inherit from something less generic than `Exception`.
    """

    pass


class ValidationError(ValueError):
    """An error with XML.

    Indicates that the XML does not conform to the IATI standard.

    Warning:
        Highly likely to change.

        This is too general to identify many specific problems.
    """

    pass
