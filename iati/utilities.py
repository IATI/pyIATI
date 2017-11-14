"""A module containing utility functions."""
import logging
import os
from io import StringIO
import chardet
from lxml import etree
import iati.constants


def add_namespace(tree, new_ns_name, new_ns_uri):
    """Add a namespace to a Schema.

    Args:
        tree (etree._ElementTree): The ElementTree to add a namespace to.

        new_ns_name (str): The name of the new namespace. Must be valid against https://www.w3.org/TR/REC-xml-names/#NT-NSAttName

        new_ns_uri (str): The URI for the new namespace. Must be non-empty and valid against https://www.ietf.org/rfc/rfc2396.txt

    Returns:
        etree.ElementTree: A copy of the provided `tree`, modified to include the specified namespace.

    Raises:
        TypeError: If an attempt is made to add a namespace to something other than a ElementTree.
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
    if not isinstance(tree, etree._ElementTree):  # pylint: disable=protected-access
        msg = "The `tree` parameter must be of type `etree._ElementTree` - it was of type {0}".format(type(tree))
        iati.utilities.log_error(msg)
        raise TypeError(msg)
    if not isinstance(new_ns_name, str) or not new_ns_name:
        msg = "The `new_ns_name` parameter must be a non-empty string."
        iati.utilities.log_error(msg)
        raise ValueError(msg)
    if not isinstance(new_ns_uri, str) or not new_ns_uri:
        msg = "The `new_ns_uri` parameter must be a valid URI."
        iati.utilities.log_error(msg)
        raise ValueError(msg)

    initial_nsmap = tree.getroot().nsmap
    # prevent modification of existing namespaces
    if new_ns_name in initial_nsmap:
        if new_ns_uri == initial_nsmap[new_ns_name]:
            return tree
        else:
            msg = "There is already a namespace called {0}.".format(new_ns_name)
            iati.utilities.log_error(msg)
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
    """Convert an etree to a Schema.

    Args:
        tree (etree._ElementTree): An XML element tree representing an XML Schema.

    Returns:
        etree.XMLSchema: The XML schema that the provided tree represented.

    Warning:
        Should raise exceptions when there are errors during execution.

        Needs to better distinguish between an `etree.XMLSchema`, an `iati.Schema`, an `iati.ActivitySchema` and an `iati.OrganisationSchema`.

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
        iati.utilities.log_error(msg)
        raise xml_syntax_err
    except ValueError:
        msg = "To parse XML into a tree, the XML must be a string, not a {0}.".format(type(xml))
        iati.utilities.log_error(msg)
        raise ValueError(msg)


def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys in a dictionary.

    RFC4627 merely says that keys in a JSON file SHOULD be unique. As such, `json.loads()` permits duplicate keys, and overwrites earlier values with those later in the string.

    In creating Rulesets, we wish to forbid duplicate keys. As such, this function may be used to do this.

    Algorithm from https://stackoverflow.com/a/14902564

    Args:
        ordered_pairs (list(tuple)): A list of (key, value) pairs.

    Raises:
        ValueError: When there are duplicate keys.

    Returns:
        dict: A dictionary constructed from `ordered_pairs`.

    """
    duplicate_free_dict = {}
    for key, value in ordered_pairs:
        if key in duplicate_free_dict:
            raise ValueError("duplicate key: %r" % (key,))
        else:
            duplicate_free_dict[key] = value
    return duplicate_free_dict


def load_as_bytes(path):
    """Load a file at the specified path into a bytes object.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        bytes: The contents of the file at the specified location.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.

    Todo:
        Ensure all reasonably possible `OSError`s are documented here and in functions that call this.

        Add error handling for when the specified file does not exist.

        Pass in PACKAGE as a default parameter, so that this code can be used by other library modules (e.g. iati.fetch).

    """
    with open(path, 'rb') as file_to_load:
        data = file_to_load.read()

    return data


def load_as_dataset(path):
    """Load a file at the specified path into a Dataset.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        iati.Dataset: A Dataset object representing the contents of the file at the specified location.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.

        ValueError: When a file at the specified path does not contain valid XML.

    Todo:
        Ensure all reasonably possible OSErrors are documented here and in functions that call this.
        Add error handling for when the specified file does not exist.

    """
    dataset_str = load_as_string(path)

    return iati.Dataset(dataset_str)


def load_as_string(path):
    """Load a file at the specified path into a string.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        str (python3) / unicode (python2): The contents of the file at the specified location.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.

    Todo:
        Pass in PACKAGE as a default parameter, so that this code can be used by other library modules (e.g. iati.fetch).

    """
    loaded_bytes = load_as_bytes(path)

    try:
        loaded_str = loaded_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # the file was not UTF-8, so perform a (slow) test to detect encoding
        # only use the first section of the file since this is generally enough and prevents big files taking ages
        detected_info = chardet.detect(loaded_bytes[:25000])
        try:
            loaded_str = loaded_bytes.decode(detected_info['encoding'])
            # in Python 2 it is necessary to strip the BOM when decoding from UTF-16BE
            if detected_info['encoding'] == 'UTF-16' and loaded_str[:1] == u'\ufeff':
                loaded_str = loaded_str[1:]
        except TypeError:
            raise ValueError('Could not detect encoding of file')

    return loaded_str


def load_as_tree(path):
    """Load a schema at the specified path into an ElementTree.

    Args:
        path (str): The path to the file that is to be converted to an ElementTree. The file at the specified location must contain valid XML.

    Returns:
        etree._ElementTree: An ElementTree representing the parsed XML.

    Raises:
        OSError: An error occurred accessing the specified file.

    Warning:
        There should be errors raised when the request is to load something that is not valid XML.

        Does not fully hide the lxml internal workings. This includes making reference to a private lxml type.

    Todo:
        Handle when the specified file can be accessed without issue, but it does not contain valid XML.

    """
    try:
        doc = etree.parse(path)
        return doc
    except OSError:
        raise


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
        filename=os.path.join(iati.constants.LOG_FILE_NAME),
        format='%(asctime)s %(levelname)s:%(name)s: %(message)s %(stack_info)s',
        level=logging.DEBUG
    )
    logger = logging.getLogger(iati.constants.LOGGER_NAME)
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


def versions_for_integer(integer):
    """Return a list containing the supported versions for the input integer version.

    Args:
        integer (int): The integer version to find the supported version for.

    Returns:
        list of str: Containing the supported versions for the input integer.

    """
    output = list()
    for version in iati.constants.STANDARD_VERSIONS:
        if version.startswith(str(integer)):
            output.append(version)

    return output
