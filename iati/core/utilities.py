"""A module containing utility functions."""
import logging
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from lxml import etree
import iati.core.constants


def add_namespace(tree, new_ns_name, new_ns_uri):
    """Add a namespace to a Schema.

    Params:
        tree (etree._ElementTree): The ElementTree to add a namespace to.
        new_ns_name (str): The name of the new namespace. Must be valid against https://www.w3.org/TR/REC-xml-names/#NT-NSAttName
        new_ns_uri (str): The URI for the new namespace. Must be non-empty and valid against https://www.ietf.org/rfc/rfc2396.txt

    Returns:
        iati.core.schemas.Schema: The provided Schema, modified to include the specified namespace.

    Raises:
        TypeError: If an attempt is made to add a namespace to something other than a Schema.
        ValueError: If the namespace name or URI are invalid values.
        ValueError: If the namespace name already exists.

    Note:
        lxml does not allow modification of namespaces within a tree that already exists. As such, string manipulation is used. https://bugs.launchpad.net/lxml/+bug/555602

    Todo:
        Also add new namespaces to Datasets.

        Add checks for the format of new_ns_name - for syntax, see: https://www.w3.org/TR/REC-xml-names/#NT-NSAttName

        Add checks for the format of new_ns_uri - for syntax, see: https://www.ietf.org/rfc/rfc2396.txt

        Tidy this up.

    """
    if not isinstance(tree, etree._ElementTree):
        msg = "The `tree` parameter must be of type `etree._ElementTree` - it was of type {0}".format(type(tree))
        iati.core.utilities.log_error(msg)
        raise TypeError(msg)
    if not isinstance(new_ns_name, str) or len(new_ns_name) == 0:
        msg = "The `new_ns_name` parameter must be a non-empty string."
        iati.core.utilities.log_error(msg)
        raise ValueError(msg)
    if not isinstance(new_ns_uri, str) or len(new_ns_uri) == 0:
        msg = "The `new_ns_name` parameter must be a valid URI."
        iati.core.utilities.log_error(msg)
        raise ValueError(msg)

    initial_nsmap = tree.getroot().nsmap
    # prevent modification of existing namespaces
    if new_ns_name in initial_nsmap:
        if new_ns_uri == initial_nsmap[new_ns_name]:
            return tree
        else:
            msg = "There is already a namespace called {0}.".format(new_ns_name)
            iati.core.utilities.log_error(msg)
            raise ValueError(msg)

    # to add new namespace, use algorithm from http://stackoverflow.com/a/11350061
    schema_str = etree.tostring(tree.getroot(), pretty_print=True).decode('unicode_escape')
    interim_tree = etree.ElementTree(element=None, file=StringIO(schema_str))
    root = interim_tree.getroot()
    nsmap = root.nsmap
    nsmap[new_ns_name] = new_ns_uri
    new_root = etree.Element(root.tag, nsmap=nsmap)
    new_root[:] = root[:]
    new_tree = etree.ElementTree(new_root)

    return new_tree


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
