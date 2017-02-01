"""A module containing a core representation of an IATI Dataset."""
from lxml import etree

class Dataset(object):
    """Representation of an IATI XML file that may be validated against a schema.

    Attributes:
        strictly_valid (bool): Whether the dataset must strictly conform to the IATI standard.
            If strictly conforming, invalid elements and attributes will be removed.
        xml_str (str): A string representation of the XML being represented.
        xml_tree (ElementTree): A tree representation of the XML being represented.

    Todo:
        xml_str and xml_tree should be attributes, not functions. Updating one should update the other.
    """

    def __init__(self, **kargs):
        """Initialise a dataset.

        Keyword args:
            strictly_valid (bool): Whether the dataset must strictly conform to the IATI standard.
                Defaults to False.
            xml_str (str): A string representation of the XML to encapsulate.
            xml_tree (ElementTree): A tree representation of the XML to encapsulate.
        """
        pass
