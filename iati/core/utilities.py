"""A module containing utility functions."""
import logging
import os
from lxml import etree
import iati.core.constants


def convert_tree_to_schema(tree):
    """Convert an etree to a schema.

    Args:
        tree (etree._ElementTree): An XML element tree representing an XML Schema.

    Returns:
        etree.XMLSchema: The XML schema that the provided tree represented.

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
    """
    log(logging.ERROR, msg, *args, **kwargs)


def log_exception(msg, *args, **kwargs):
    """Log an exception.

    An exception is like an error, but with a stack trace.

    Args:
        msg (str): The message that is to be logged.
        *args
        **kwargs
    """
    log(logging.ERROR, msg, exc_info=True, *args, **kwargs)


def log_warning(msg, *args, **kwargs):
    """Log a warning.

    Args:
        msg (str): The message that is to be logged.
        *args
        **kwargs
    """
    log(logging.WARN, msg, *args, **kwargs)
