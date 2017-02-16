"""A module containing a core representation of IATI Codelists."""
from lxml import etree
import iati.core.resources
import iati.core.utilities


def fetch_mappings():
    """Fetch the mappings between Codelists and XPaths.

    These mappings make it possible to work out which attributes within the Schema are to be validated against a given Codelist.

    Returns:
        dict: A dictionary of mappings from XPaths (keys) to a (ref, condition) tuple (values). The condition part of the tuple is optional, and so will be None if there is no attached condition.

    Warning:
        The format of the return value is likely to change to better match actual use cases.

    Todo:
        Determine alternative formats that the mappings may be returned in, such as the basic string or tree.

        Error handling.

        Add parsing of the (optional) 'condition' element.
    """
    tree = iati.core.resources.load_as_tree(iati.core.resources.PATH_CODELIST_MAPPINGS)

    mappings = {}
    for mapping_el in tree.findall('mapping'):
        path = mapping_el.find('path').text
        ref = mapping_el.find('codelist').get('ref')
        mappings[path] = (ref, None)

    return mappings


class Codelist(object):
    """Representation of a Codelist as defined within the IATI SSOT.

    Attributes:
        codes (:obj:`list` of :obj:`iati.core.codelists.Code`): The codes demonstrating the range of values that the Codelist may represent.
        name (str): The name of the Codelist.

    Private Attributes:
        _path (str): A path to a file containing a Codelist in XML form.

    Note:
        The _path attribute may be removed.

    Warning:
        There are currently a large number of attributes that have been taken straight from the XML without being implemented in code. Some of these may change during implementation.

        The `codes` attribute is currently a list. While this class is called a CodeLIST, a list may not be the most appropriate datatype - something like a dict or set may be better.

    Todo:
        Provide functionality to allow XML to be loaded from a parameter-defined path.

        Implement and document attributes that are not yet implemented and documented.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, path=None, xml=None):
        """Initialise a Codelist.

        Any Codes contained within the specified XML are added.
        Any Codes contained within the file at the specified path are added.

        Args:
            name (str): The name of the codelist being initialised.
            path (str): A path to a file containing a valid codelist in XML format.
            xml (str): An XML representation of a codelist.

        Note:
            Instances of a Codelist should remain independent of a particular version of the IATI Standard. Versioning should be handled elsewhere.

        Warning:
            The format of the constructor is likely to change. It needs to be less reliant on the name acting as a UID,  and allow for other attributes to be defined.

        Todo:
            Raise warnings or errors if the Codelist is unable to initialise correctly.
        """
        def parse_from_xml(xml):
            """Parse a Codelist from the XML that defines it.

            Warning:
                In modifying the parameters required for creating an instance of the class, this is likely to move in some manner.

            Todo:
                Define relevant tests and error handling.

                Handle Codelists without description or name elements.

                Better document side-effects.
            """
            tree = iati.core.utilities.convert_xml_to_tree(xml)

            self.name = tree.attrib['name']
            for code_el in tree.findall('codelist-items/codelist-item'):
                value = code_el.find('code').text
                name = 'tmp'
                # name = code_el.find('description/narrative').text
                self.add_code(iati.core.codelists.Code(value, name))

        self.codes = []
        self.name = name
        self._path = path

        self.name_prose = None
        self.description = None
        self.language = None
        self.url = None
        self.ref = None
        self.category_codelist = None
        self.complete = None

        if xml:
            parse_from_xml(xml)

    def __eq__(self, other):
        """Check Codelist equality.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise the contained Codes as part of the equality process.
        """
        return (self.name) == (other.name)

    def __hash__(self):
        """Hash the Codelist.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise the contained Codes as part of the hashing process.
        """
        return hash((self.name))

    def add_code(self, code):
        """Add a Code to the Codelist.

        Args:
            code (iati.core.codelists.Code): The Code to add to the Codelist.

        Warning:
            At present this is merely acting as a wrapper for a list. The current state of the TODO indicates that it may be better as a set. In that instance, this function may not be required.

        Todo:
            Prohibit duplicate Codes being added to a Codelist.
        """
        if isinstance(code, Code):
            self.codes.append(code)

    def xsd_tree(self):
        """Output the Codelist as an XSD etree type.

        This tree may be used to specify the type of given elements, allowing insertion and validation within a schema.

        Returns:
            etree.Element: An XSD simpleType representing this Codelist.

        Warning:
            It is planned to change from Schema-based to Data-based Codelist validation. As such, this function may be removed.

            The name attribute of the generated type is not good and needs changing.

            Does not fully hide the lxml internal workings.

        Todo:
            See whether there are only Codelists of a type other than string.

            Improve naming of the type to reduce potential of clashes.

            Rename this function, potentially making it a property.
        """
        type_base_el = etree.Element(
            iati.core.constants.NAMESPACE + 'simpleType',
            name='{0}-type'.format(self.name),
            nsmap=iati.core.constants.NSMAP
        )
        restriction_base_el = etree.Element(
            iati.core.constants.NAMESPACE + 'restriction',
            base='xsd:string',
            nsmap=iati.core.constants.NSMAP
        )

        for code in self.codes:
            restriction_base_el.append(code.xsd_tree())

        type_base_el.append(restriction_base_el)

        return type_base_el


class Code(object):
    """Representation of a Code contained within a Codelist.

    Attributes:
        name (str): The name of the code.
        value (str): The value of the code.

    Todo:
        Implement and document attributes that are not yet implemented and documented.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, value=None, name=None):
        """Initialise a Code.

        Args:
            name (str): The name of the code being initialised.
            value (str): The value of the code being initialised.

        Note:
            Instances of a Code should remain independent of a particular version of the IATI Standard. Versioning should be handled elsewhere.

        Warning:
            The format of the constructor is likely to change. It should include mandatory parameters, and allow for other attributes to be defined.
        """
        self.name = name
        self.value = value

        self.description = None
        self.category = None
        self.url = None
        self.public_database = False
        self.status = None
        self.activation_date = None
        self.withdrawal_date = None

    def __eq__(self, other):
        """Check Code equality.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes equality process.
        """
        return ((self.name) == (other.name)) and ((self.value) == (other.value))

    def __hash__(self):
        """Hash the Code.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes as part of the hashing process.
        """
        return hash((self.name, self.value))

    def xsd_tree(self):
        """Output the Code as an etree enumeration element.

        Warning:
            It is planned to change from Schema-based to Data-based Codelist validation. As such, this function may be removed.

            Does not fully hide the lxml internal workings.

        Todo:
            Rename this function, potentially making it a property.
        """
        return etree.Element(
            iati.core.constants.NAMESPACE + 'enumeration',
            value=self.value,
            nsmap=iati.core.constants.NSMAP
        )
