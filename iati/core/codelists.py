"""A module containing a core representation of IATI Codelists."""
import iati.core.resources
import iati.core.utilities


class Codelist(object):
    """Representation of a Codelist as defined within the IATI SSOT.

    Attributes:
        codes (:obj:`list` of :obj:`iati.core.codelists.Code`): The codes demonstrating the range of values that the Codelist may represent.
        name (str): The name of the Codelist.
        path (str): A path to a file containing a Codelist in XML form.

    Note:
        The path attribute may be removed.

    Todo:
        Provide functionality to allow XML to be loaded from a parameter-defined path.
    """

    def __init__(self, name, path=None, xml=None):
        """Initialise a Codelist.

        Any Codes contained within the specified XML are added.
        Any Codes contained within the file at the specified path are added.

        Args:
            name (str): The name of the codelist being initialised.
            path (str): A path to a file containing a valid codelist in XML format.
            xml (str): An XML representation of a codelist.

        Todo:
            Raise warnings or errors if the Codelist is unable to initialise correctly.
        """
        def parse_from_xml(xml):
            """Parse a Codelist from the XML that defines it.

            Todo:
                Define relevant tests and error handling.
            """
            tree = iati.core.utilities.convert_xml_to_tree(xml)

            self.name = tree.attrib['name']
            for code_el in tree.findall('codelist-items/codelist-item'):
                value = code_el.find('code').text
                name = code_el.find('description/narrative').text
                self.add_code(iati.core.codelists.Code(value, name))

        self.codes = []
        self.name = name
        self.path = path

        if xml:
            parse_from_xml(xml)

    def __eq__(self, other):
        """Check Codelist equality.

        Todo:
            Utilise the contained Codes as part of the equality process.
        """
        return (self.name) == (other.name)

    def __hash__(self):
        """Hash the Codelist.

        Todo:
            Utilise the contained Codes as part of the hashing process.
        """
        return hash((self.name))

    def add_code(self, code):
        """Add a Code to the Codelist.

        Args:
            code (iati.core.codelists.Code): The Code to add to the Codelist.

        Todo:
            Prohibit duplicate Codes being added to a Codelist.
        """
        if isinstance(code, Code):
            self.codes.append(code)


class Code(object):
    """Representation of a Code contained within a Codelist.

    Attributes:
        name (str): The name of the code.
        value (str): The value of the code.

    Todo:
        Add other possible attributes.
    """

    def __init__(self, value=None, name=None):
        """Initialise a Code.

        Args:
            name (str): The name of the code being initialised.
            value (str): The value of the code being initialised.
        """
        self.name = name
        self.value = value
