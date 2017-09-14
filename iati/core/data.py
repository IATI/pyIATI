"""A module containing a core representation of an IATI Dataset."""
import sys
from lxml import etree
import iati.core.exceptions
import iati.core.utilities


class Dataset(object):
    """Representation of an IATI XML file that may be validated against a schema.

    Attributes:
        xml_str (str): A string representation of the XML being represented.
        xml_tree (ElementTree): A tree representation of the XML being represented.

    Note:
        The current content of the dataset is deemed to be that which was last asigned to either `self.xml_str` or `self.xml_tree`.

    Warning:
        The behaviour of simultaneous assignment to both `self.xml_str` and `self.xml_tree` is undefined.

        `xml_str` and `xml_tree` are not great names. They are also too tied together. It should be determined whether this close relationship is really desired.

        Does not fully hide the lxml internal workings.

    Todo:
        Implement getters and setters for attributes.

        Implement an addition override to allow for combation of datasets.

    """

    def __init__(self, xml):
        """Initialise a dataset.

        Args:
            xml (str/ElementTree): A representation of the XML to encapsulate.
                May be either a string or an ElementTree.

        Raises:
            TypeError: If an attempt to pass something that is not a string or ElementTree is made.
            ValueError: If a provided XML string is not valid XML.
            iati.core.exceptions.ValidationError:
                If the provided XML should conform to the IATI standard, but does not.

        Warning:
            It should be possible to create a dataset from a file. In this situation, having `xml` as a required parameter does not seem sensible. Need to better consider this situation.

        Todo:
            Undertake validation.
            Add a way to determine whether a dataset fully conforms to the IATI standard and / or modify the dataset so that it does.

        """
        self._xml_str = None
        self._xml_tree = None

        if isinstance(xml, etree._Element):  # pylint: disable=W0212
            self.xml_tree = xml
        else:
            self.xml_str = xml

    @property
    def xml_str(self):
        """Return a string representation of the XML being represented.

        Raises:
            ValueError: If a value that is being assigned is not a valid XML string.
            TypeError: If a value that is being assigned is not a string at all.

        Todo:
            Clarify error messages, for example when a mismatched encoding is used.
            Perhaps pass on the original lxml error message instead of trying to intrepret what might have gone wrong when running etree.fromstring.

        """
        return self._xml_str

    @xml_str.setter
    def xml_str(self, value):
        if isinstance(value, etree._Element):  # pylint: disable=W0212
            msg = "If setting a dataset with an ElementTree, use the xml_tree property, not the xml_str property."
            iati.core.utilities.log_error(msg)
            raise TypeError(msg)
        else:
            try:
                value_stripped = value.strip()

                # Convert the input to bytes, as etree.fromstring works most consistently with bytes objects, especially if an XML encoding declaration has been used.
                if (isinstance(value_stripped, str) and
                        sys.version_info.major > 2):  # Python v2 treats strings as byte objects by default
                    value_stripped_bytes = value_stripped.encode()
                else:
                    value_stripped_bytes = value_stripped

                self.xml_tree = etree.fromstring(value_stripped_bytes)
                self._xml_str = value_stripped
            except etree.XMLSyntaxError:
                msg = "The string provided to create a Dataset from is not valid XML."
                iati.core.utilities.log_error(msg)
                raise ValueError(msg)
            except (AttributeError, TypeError, ValueError):
                msg = "Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type: {0}".format(type(value))
                iati.core.utilities.log_error(msg)
                raise TypeError(msg)

    @property
    def xml_tree(self):
        """Return a tree representation of the XML being represented.

        Raises:
            TypeError: If a value that is being assigned is not an ElementTree.

        Warning:
            Does not fully hide the lxml internal workings.

        Todo:
            Check use of ElementTree in setter.

        """
        return self._xml_tree.getroottree()

    @xml_tree.setter
    def xml_tree(self, value):
        if isinstance(value, etree._Element):  # pylint: disable=W0212
            self._xml_tree = value
            self._xml_str = etree.tostring(value, pretty_print=True)
        else:
            msg = "If setting a dataset with the xml_property, an ElementTree should be provided, not a {0}.".format(type(value))
            iati.core.utilities.log_error(msg)
            raise TypeError(msg)

    def _raw_source_at_line(self, line_number):
        """Return the raw value of the XML source at the specified line.

        Args:
            line_number (int): A zero-indexed line number.

        Returns:
            str: The source of the XML at the specified line.

        Raises:
            TypeError: When `line_number` is not an integer.
            ValueError: When `line_number` is negative or more than the number of lines in the file.

        """
        if not isinstance(line_number, int) or isinstance(line_number, bool):
            raise TypeError

        if line_number < 0:
            raise ValueError

        try:
            # this is led with an empty string since the `sourceline` attribute is 1-indexed.
            split_lines = [''] + self.xml_str.split('\n')
            return split_lines[line_number]
        except IndexError:
            raise ValueError

    @property
    def version(self):
        """The version that this Dataset is specified against.

        Returns:
            str / None: The version of this Dataset. None if the version cannot be detected.

        Todo:
            Consider if this should raise an error if the Dataset is specified at a version that does not exist.

        """
        root_tree = self.xml_tree.getroot()
        assumed_version_if_no_version_stated = '1.01'
        version_iati_root = root_tree.get('version', assumed_version_if_no_version_stated)

        if version_iati_root.startswith('1'):
            # Version 1 data, so need to check that all child `iati-activity` elements are at the same version
            versions_in_children = list()
            for child_tree in root_tree.findall('iati-activity'):
                activity_version = child_tree.get('version', assumed_version_if_no_version_stated)
                versions_in_children.append(activity_version)

            if len(set(versions_in_children)) == 1 and versions_in_children[0] == version_iati_root:
                return version_iati_root
            else:
                return None
        else:
            # Not version 1 data, so can return the version specified in `iati-activities/@version`
            return version_iati_root

    def source_at_line(self, line_number):
        """Return the value of the XML source at the specified line.

        Args:
            line_number (int): A zero-indexed line number.

        Returns:
            str: The source of the XML at the specified line. Leading and trailing whitespace is trimmed.

        Raises:
            TypeError: When `line_number` is not an integer.
            ValueError: When `line_number` is negative or more than the number of lines in the file.

        Todo:
            Test with minified XML.

        """
        return self._raw_source_at_line(line_number).strip()

    def source_around_line(self, line_number, surrounding_lines=1):
        """Return the value of the XML source at the specified line, plus the specified amount of surrounding context.

        Args:
            line_number (int): A zero-indexed line number.
            surrounding_lines (int): The number of lines of context to provide either side of the specified line number. Default 1.

        Returns:
            str: The source of the XML at the specified line, plus the specified number of lines of surrounding context.
            Should there be fewer lines of XML than are asked for, the entire Dataset will be returned.

        Raises:
            TypeError: When `line_number` is not an integer.
            TypeError: When `surrounding_lines` is not an integer.
            ValueError: When `line_number` is negative or more than the number of lines in the file.
            ValueError: When `surrounding_lines` is negative.

        Todo:
            Test with minified XML.

        """
        if not isinstance(surrounding_lines, int) or isinstance(surrounding_lines, bool):
            raise TypeError

        if surrounding_lines < 0:
            raise ValueError

        lines_arr = []
        lower_line_number = max(line_number - surrounding_lines, 1)
        upper_line_number = min(line_number + surrounding_lines + 1, len(self.xml_str.split('\n')) + 1)

        for line_num in range(lower_line_number, upper_line_number):
            lines_arr.append(self._raw_source_at_line(line_num))

        return '\n'.join(lines_arr)
