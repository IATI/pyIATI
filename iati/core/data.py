"""A module containing a core representation of an IATI Dataset."""
from lxml import etree
import iati.core.exceptions
import iati.core.utilities


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

    def __init__(self, xml, strictly_valid=False):
        """Initialise a dataset.

        Args:
            xml (str/ElementTree): A representation of the XML to encapsulate.
                May be either a string or an ElementTree.
            strictly_valid (bool, optional): Whether the dataset must strictly conform to the IATI standard.
                Defaults to False.

        Raises:
            TypeError: If an attempt to pass something that is not a string or ElementTree is made.
            ValueError: If a provided XML string is not valid XML.
            iati.core.exceptions.ValidationError:
                If the provided XML should conform to the IATI standard, but does not.

        Todo:
            Undertake validation.
        """
        if isinstance(xml, etree._Element):
            self.xml_tree = xml
            self.xml_str = etree.tostring(xml)
        else:
            self.xml_str = xml
            try:
                self.xml_tree = etree.fromstring(xml)
            except etree.XMLSyntaxError:
                msg = "The string provided to create a Dataset from is not valid XML."
                iati.core.utilities.log_error(msg)
                raise ValueError(msg)
            except ValueError:
                msg = "Datasets can only be created from ElementTrees or strings containing valid XML. Actual type: {0}".format(type(xml))
                iati.core.utilities.log_error(msg)
                raise TypeError(msg)
