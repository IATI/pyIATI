"""A module containing a core representation of IATI Codelists."""
import collections
from lxml import etree
import iati.resources
import iati.utilities


class Codelist:
    """Representation of a Codelist as defined within the IATI SSOT.

    Attributes:
        complete (bool): Whether the Codelist is complete or not. If complete, attributes making use of this Codelist must only contain values present on the Codelist. If not complete, this is merely strongly advised.
        codes (:obj:`set` of :obj:`iati.Code`): The codes demonstrating the range of values that the Codelist may represent.
        name (str): The name of the Codelist.

    Warning:
        There are currently a large number of attributes that have been taken straight from the XML without being implemented in code. Some of these may change during implementation.

        The `codes` attribute is currently a set. While functionally correct, it may be slightly confusing because the class is a CodeLIST.

    Todo:
        Create a custom class inheriting from set that only allows Codes to be added.

        Implement and document attributes that are not yet implemented and documented.

    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, xml=None):
        """Initialise a Codelist.

        Any Codes contained within the specified XML are added.

        Args:
            name (str): The name of the codelist being initialised.
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
            tree = iati.utilities.convert_xml_to_tree(xml)

            self.name = tree.attrib['name']
            for code_el in tree.findall('codelist-items/codelist-item'):
                value = code_el.findtext('code')
                name = code_el.findtext('name/narrative') or code_el.findtext('name')

                if (value is None) and (name is None):
                    msg = "The provided Codelist ({0}) has a Code that does not contain a name or value.".format(self.name)
                    iati.utilities.log_warning(msg)

                if value is None:
                    value = ''
                if name is None:
                    name = ''
                self.codes.add(iati.Code(value, name))

            try:
                self.complete = True if tree.attrib['complete'] == '1' else False
            except KeyError:
                pass

        self.complete = None
        self.codes = set()
        self.name = name

        # a number of placeholder attributes that Codelists have, though are not yet implemented
        self._name_prose = None
        self._description = None
        self._language = None
        self._url = None
        self._ref = None
        self._category_codelist = None

        if xml:
            parse_from_xml(xml)

    def __eq__(self, other):
        """Check Codelist equality.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes as part of the equality process.

        """
        return (self.name == other.name) and (self.complete == other.complete) and (collections.Counter(self.codes) == collections.Counter(other.codes))

    def __ne__(self, other):
        """Check Codelist inequality."""
        return not self == other

    def __hash__(self):
        """Hash the Codelist.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes as part of the equality process.

        """
        sorted_codes = sorted(self.codes, key=lambda x: x.value)

        return hash((self.name, self.complete, tuple(sorted_codes)))

    @property
    def xsd_restriction(self):
        """Output the Codelist as an XSD simpleType restriction.

        This tree may be used to specify the type of given elements, allowing insertion and validation within a Schema.

        Returns:
            etree.Element: An XSD simpleType representing this Codelist.

        Warning:
            It is planned to change from Schema-based to Data-based Codelist validation. As such, this property may be removed.

            The name attribute of the generated type is not good and needs changing.

            Does not fully hide the lxml internal workings.

        Todo:
            See whether there are only Codelists of a type other than string.

            Improve naming of the type to reduce potential of clashes.

        """
        type_base_el = etree.Element(
            iati.constants.NAMESPACE + 'simpleType',
            name='{0}-type'.format(self.name),
            nsmap=iati.constants.NSMAP
        )
        restriction_base_el = etree.Element(
            iati.constants.NAMESPACE + 'restriction',
            base='xsd:string',
            nsmap=iati.constants.NSMAP
        )

        for code in self.codes:
            restriction_base_el.append(code.xsd_enumeration)

        type_base_el.append(restriction_base_el)

        return type_base_el


class Code:
    """Representation of a Code contained within a Codelist.

    Attributes:
        name (str): The name of the code.
        value (str): The value of the code.

    Todo:
        Implement and document attributes that are not yet implemented and documented.

    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, value, name=''):
        """Initialise a Code.

        Args:
            value (str): The value of the code being initialised.
            name (str): The name of the code being initialised.

        Note:
            Instances of a Code should remain independent of a particular version of the IATI Standard. Versioning should be handled elsewhere.

        Warning:
            The format of the constructor is likely to change. It should include mandatory parameters, and allow for other attributes to be defined.

        """
        self.name = name
        self.value = value

        # a number of placeholder attributes that Codelists have, though are not yet implemented
        self._description = None
        self._category = None
        self._url = None
        self._public_database = False
        self._status = None
        self._activation_date = None
        self._withdrawal_date = None

    def __eq__(self, other):
        """Check Code equality.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes as part of the equality process.

            Test comparison with strings.

        """
        try:
            return ((self.name) == (other.name)) and ((self.value) == (other.value))
        except AttributeError:
            return self.value == other

    def __ne__(self, other):
        """Check Code inequality."""
        return not self == other

    def __hash__(self):
        """Hash the Code.

        This allows uniqueness to be correctly defined upon insertion into a set.

        Todo:
            Utilise all attributes as part of the hashing process.

            Be able to deal with checks against both Codes and strings.

        """
        return hash((self.value))

    @property
    def xsd_enumeration(self):
        """Output the Code as an etree enumeration element.

        Returns:
            etree.Element: An XSD enumeration representing this Codelist.

        Warning:
            It is planned to change from Schema-based to Data-based Codelist validation. As such, this property may be removed.

            Does not fully hide the lxml internal workings.

        """
        return etree.Element(
            iati.constants.NAMESPACE + 'enumeration',
            value=self.value,
            nsmap=iati.constants.NSMAP
        )
