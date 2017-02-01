"""A module containing a core representation of an IATI Dataset."""
from lxml import etree
import iati.core.exceptions

class Dataset(object):
    """Representation of an IATI XML file that may be validated against a schema.

    Attributes:
        strictly_valid (bool): Whether the dataset must strictly conform to the IATI standard.
            If strictly conforming, invalid elements and attributes will be removed.
        xml_str (str): A string representation of the XML being represented.
        xml_tree (ElementTree): A tree representation of the XML being represented.

    Todo:
        Implement getters and setters for attributes.
    """

    def __init__(self, **kargs):
        """Initialise a dataset.

        Keyword args:
            strictly_valid (bool): Whether the dataset must strictly conform to the IATI standard.
                Defaults to False.
            xml (str/ElementTree): A representation of the XML to encapsulate.
                May be either a string or an ElementTree.

        Raises:
            ValueError: If a provided XML string is not valid XML.
            iati.core.exceptions.ValidationError:
                If the provided XML should conform to the IATI standard, but does not.

        Todo:
            Implement this function.
            Undertake validation.
        """
        pass
