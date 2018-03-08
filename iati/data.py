"""A module containing a core representation of an IATI Dataset."""
import sys
from lxml import etree
import iati.exceptions
import iati.utilities
import iati.validator


class Dataset(object):
    """Representation of an IATI XML file that may be validated against a Schema.

    Attributes:
        xml_str (str): An XML string representation of the Dataset.
        xml_tree (ElementTree): A tree representation of the Dataset.

    Note:
        Should it be modified after initialisation, the current content of the Dataset is deemed to be that which was last asigned to either `self.xml_str` or `self.xml_tree`.

    Warning:
        The behaviour of simultaneous assignment to both `self.xml_str` and `self.xml_tree` is undefined.

        Does not fully hide the lxml internal workings.

    Todo:
        `xml_str` and `xml_tree` are not great names. They are also too tied together. It should be determined whether this close relationship is really desired.

        Implement a number of helper functions for common operations.

        Implement getters and setters for attributes.

        Implement an addition override to allow for combation of Datasets.

    """

    def __init__(self, xml):
        """Initialise a Dataset.

        Args:
            xml (str or ElementTree): A representation of the XML to encapsulate.
                May be either a string or a lxml ElementTree.

        Raises:
            TypeError: If an attempt to pass something that is not a string or ElementTree is made.
            ValueError: If a provided XML string is not valid XML.

        Warning:
            The required parameters to create a Dataset may change. See the TODO.

        Todo:
            It should be possible to create a Dataset from a file. In this situation, having `xml` as a required parameter does not seem sensible. Need to better consider this situation.

            Add a way to determine whether a Dataset fully conforms to the IATI Standard and / or modify the Dataset so that it does.

        """
        self._xml_str = None
        self._xml_tree = None

        if isinstance(xml, (etree._Element, etree._ElementTree)):  # pylint: disable=W0212
            self.xml_tree = xml
        else:
            self.xml_str = xml

    @property
    def xml_str(self):
        """str: An XML string representation of the Dataset.

        Raises:
            ValueError: If a value that is being assigned is not a valid XML string.
            TypeError: If a value that is being assigned is not a string.

        Todo:
            Clarify error messages, for example when a mismatched encoding is used.

            Perhaps pass on the original lxml error message instead of trying to intrepret what might have gone wrong when running `etree.fromstring()`.

        """
        return self._xml_str

    @xml_str.setter
    def xml_str(self, value):
        if isinstance(value, (etree._Element, etree._ElementTree)):  # pylint: disable=W0212
            msg = "If setting a Dataset with an ElementTree, use the xml_tree property, not the xml_str property."
            iati.utilities.log_error(msg)
            raise TypeError(msg)
        else:
            try:
                value_stripped = value.strip()

                validation_error_log = iati.validator.validate_is_xml(value_stripped)

                # Convert the input to bytes, as etree.fromstring works most consistently with bytes objects, especially if an XML encoding declaration has been used.
                if (isinstance(value_stripped, str) and
                        sys.version_info.major > 2):  # Python v2 treats strings as byte objects by default
                    value_stripped_bytes = value_stripped.encode()
                else:
                    value_stripped_bytes = value_stripped

                if not validation_error_log.contains_errors():
                    self.xml_tree = etree.fromstring(value_stripped_bytes)
                    self._xml_str = value_stripped
                else:
                    if validation_error_log.contains_error_of_type(TypeError):
                        raise TypeError
                    else:
                        raise iati.exceptions.ValidationError(validation_error_log)
            except (AttributeError, TypeError):
                msg = "Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type: {0}".format(type(value))
                iati.utilities.log_error(msg)
                raise TypeError(msg)

    @property
    def xml_tree(self):
        """ElementTree: A tree representation of the Dataset.

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
        elif isinstance(value, etree._ElementTree):  # pylint: disable=W0212
            root = value.getroot()
            self._xml_tree = root
            self._xml_str = etree.tostring(root, pretty_print=True)
        else:
            msg = "If setting a Dataset with the xml_property, an ElementTree should be provided, not a {0}.".format(type(value))
            iati.utilities.log_error(msg)
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
        """Return the version of the Standard that this Dataset is specified against.

        Returns:
            str or None: The version of the Standard that this Dataset is specified against. None if the version cannot be detected.

        Todo:
            Consider if this should raise an error if the Dataset is specified at a version of the Standard that does not exist.

        """
        root_tree = self.xml_tree.getroot()
        default_version = '1.01'
        version_iati_root = root_tree.get('version', default_version).strip()

        if version_iati_root.startswith('1'):
            # Version 1 data, so need to check that all child `iati-activity` or `iati-organisation` elements are at the same version
            versions_in_children = list()
            for child_tree in root_tree.getchildren():  # This is expected to return a list of `iati-activity` or `iati-organisation` elements.
                activity_version = child_tree.get('version', default_version).strip()
                versions_in_children.append(activity_version)

            if len(set(versions_in_children)) == 1 and versions_in_children[0] == version_iati_root:
                version = version_iati_root
            else:
                version = None
        else:
            # Not version 1 data, so can return the version specified in `iati-activities/@version`
            version = version_iati_root

        return version

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
