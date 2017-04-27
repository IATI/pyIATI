"""A module containing utility functions."""
import logging
import os
from lxml import etree
import iati.core.constants


def add_namespace(schema, new_ns_name, new_ns_uri):
    """Add a namespace to a Schema.

    Params:
        schema ()

    Returns:
        iati.core.schemas.Schema: The provided Schema, modified to include the specified namespace.

    Raises:
        TypeError: If an attempt it made to add a namespace to something other than a Schema.
        ValueError: If the namespace name or uri are invalid values.

    Note:
        lxml does not allow modification of namespaces within a tree that already exists. As such, string manipulation is used. https://bugs.launchpad.net/lxml/+bug/555602

    Todo:
        Also add new namespaces to Datasets.

        Add checks for the format of new_ns_name - for syntax, see: https://www.w3.org/TR/REC-xml-names/#NT-NSAttName

        Add checks for the format of new_ns_uri - for syntax, see: https://www.ietf.org/rfc/rfc2396.txt
    """
    if not isinstance(schema, iati.core.schemas.Schema):
        msg = "The `schema` parameter must be of type `iati.core.schemas.Schema - it was of type {0}".format(type(schema))
        iati.core.utilities.log_error(msg)
        raise TypeError
    if not isinstance(new_ns_name, str) or len(new_ns_name) == 0:
        msg = "The `new_ns_name` parameter must be a non-empty string."
        iati.core.utilities.log_error(msg)
        raise ValueError
    if not isinstance(new_ns_uri, str) or len(new_ns_uri) == 0:
        msg = "The `new_ns_name` parameter must be a valid URI."
        iati.core.utilities.log_error(msg)
        raise ValueError

    initial_nsmap = schema._schema_base_tree.getroot().nsmap


def convert_tree_to_schema(tree):
    """Convert an etree to a schema.

    Args:
        tree (etree._ElementTree): An XML element tree representing an XML Schema.

    Returns:
        etree.XMLSchema: The XML schema that the provided tree represented.

    Warning:
        Should raise exceptions when there are errors during execution.

        Needs to better distinguish between an `etree.XMLSchema` and an `iati.core.schemas.Schema`.

        Does not fully hide the lxml internal workings.

    Todo:
        Surround schema conversion with error handling.
    """
    return etree.XMLSchema(tree)


def convert_xml_to_tree(xml):
    """Convert an XML string into an etree.

    Args:
        xml (str): An XML string to be converted.

    Returns:
        etree._Element: An lxml element tree representing the provided XML.

    Warning:
        Does not fully hide the lxml internal workings.

    Raises:
        ValueError: The XML provided was something other than a string.
        lxml.etree.XMLSyntaxError: There was an error with the syntax of the provided XML.
    """
    try:
        tree = etree.fromstring(xml)
        return tree
    except etree.XMLSyntaxError as xml_syntax_err:
        msg = "There was a problem with the provided XML, and it could therefore not be turned into a tree."
        iati.core.utilities.log_error(msg)
        raise xml_syntax_err
    except ValueError:
        msg = "To parse XML into a tree, the XML must be a string, not a {0}.".format(type(xml))
        iati.core.utilities.log_error(msg)
        raise ValueError(msg)


def log(lvl, msg, *args, **kwargs):
    """Log a message of some level.

    Args:
        lvl (int): The level of message being logged.
        msg (str): The message that is to be logged.
        *args
        **kwargs

    Warning:
        Potentially too tightly coupled to the Python `logging` module.

        Logging needs to be defined in a much more useful and configurable manner.

        Logging should not fill up logfiles at lightspeed unless this is specifically desired.

        Outputs should be more easily parsable.
    """
    logging.basicConfig(
        filename=os.path.join(iati.core.constants.LOG_FILE_NAME),
        format='%(asctime)s %(levelname)s:%(name)s: %(message)s %(stack_info)s',
        level=logging.DEBUG
    )
    logger = logging.getLogger(iati.core.constants.LOGGER_NAME)
    logger.log(lvl, msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    """Log an error.

    Args:
        msg (str): The message that is to be logged.
        *args
        **kwargs

    Warning:
        Potentially too tightly coupled to the Python `logging` module.
    """
    log(logging.ERROR, msg, *args, **kwargs)


def log_exception(msg, *args, **kwargs):
    """Log an exception.

    An exception is like an error, but with a stack trace.

    Args:
        msg (str): The message that is to be logged.
        *args
        **kwargs

    Warning:
        Potentially too tightly coupled to the Python `logging` module.
    """
    log(logging.ERROR, msg, exc_info=True, *args, **kwargs)


def log_warning(msg, *args, **kwargs):
    """Log a warning.

    Args:
        msg (str): The message that is to be logged.
        *args
        **kwargs

    Warning:
        Potentially too tightly coupled to the Python `logging` module.
    """
    log(logging.WARN, msg, *args, **kwargs)
