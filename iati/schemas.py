"""A module containing a core representation of IATI Schemas."""
from collections import OrderedDict
from copy import copy
from lxml import etree
import iati.codelists
import iati.constants
import iati.exceptions
import iati.resources
import iati.utilities


class Schema(object):
    """Representation of a Schema as defined within the IATI SSOT. This is used as a base class for ActivitySchema and OrganisationSchema and should not be instantiated directly.

    Attributes:
        codelists (set): The Codelists associated with this Schema.
        rulesets (set): The Rulesets associated with this Schema.
        ROOT_ELEMENT_NAME (str): The name of the root element within the XML Schema that the class represents.

    Warning:
        The private attribute allowing access to the base Schema Tree is likely to change in determining a good way of accessing the contained schema content.

    Todo:
        Determine a good API for accessing the XMLSchema that the iati.Schema represents.

    """

    ROOT_ELEMENT_NAME = ''

    def __init__(self, path):
        """Initialise a Schema.

        Args:
            path (str): The path to the Schema that is being initialised.

        Raises:
            iati.exceptions.SchemaError: An error occurred during the creation of the Schema.

        Warning:
            The format of the constructor is likely to change. It needs to be less reliant on the name acting as a UID, and allow for other attributes to be provided at this point.

            The raised exceptions are likely to change upon review of IATI-specific exceptions.

            Need to define a good API for accessing public and private attributes. Requiring something along the lines of `schema.schema` is likely not ideal. An improved understanding of use cases will be required for this.

        Todo:
            Better use the try-except pattern.

            Allow the base schema to be modified after initialisation.

            Create test instance where the SchemaError is raised.

        """
        self._schema_base_tree = None
        self._source_path = path
        self.codelists = set()
        self.rulesets = set()

        try:
            loaded_tree = iati.resources.load_as_tree(path)
        except OSError:
            msg = "Failed to load tree at '{0}' when creating Schema.".format(path)
            iati.utilities.log_error(msg)
            raise iati.exceptions.SchemaError
        else:
            self._schema_base_tree = loaded_tree
            self._flatten_includes()
            self._xsd_lookup = self._build_xsd_lookup_dict()
            self._xpath_lookup = self._build_xpath_parent_child_dict()

    def _change_include_to_xinclude(self, tree):
        """Change the method in which common elements are included.

        lxml does not contain functionality to access elements within imports defined along the lines of: `<xsd:include schemaLocation="NAME.xsd" />`
        It does, however, contains functionality to access elements within imports defined along the lines of: `<xi:include href="NAME.xsd" parse="xml" />`
        when there is a namespace defined against the root schema element as `xmlns:xi="http://www.w3.org/2001/XInclude"`

        This changes instances of the former to the latter.

        Args:
            tree (etree._ElementTree): The tree within which xsd:include is to be changed to xi:include.

        Returns:
            etree._ElementTree: The modified tree.

        Todo:
            Add more robust tests for schemas at different versions.

            Check whether this is safe in the general case, so allowing it to be performed in __init__().

            Make resource locations more able to handle the general case.

            Consider moving this out of Schema().

            Tidy this up.

            Consider using XSLT.

        """
        # identify the old info
        include_xpath = (iati.constants.NAMESPACE + 'include')
        include_el = tree.getroot().find(include_xpath)
        if include_el is None:
            return
        include_location = include_el.attrib['schemaLocation']

        # add namespace for XInclude
        xi_name = 'xi'
        xi_uri = 'http://www.w3.org/2001/XInclude'
        iati.utilities.add_namespace(tree, xi_name, xi_uri)
        new_nsmap = {}
        for key, value in iati.constants.NSMAP.items():
            new_nsmap[key] = value
        new_nsmap[xi_name] = xi_uri

        # create a new element
        xinclude_el = etree.Element(
            '{' + xi_uri + '}include',
            href=iati.resources.resource_filename(iati.resources.get_schema_path(include_location[:-4], self._get_version())),
            parse='xml',
            nsmap=new_nsmap
        )

        # make the path to `xml.xsd` reference the correct file
        import_xpath = (iati.constants.NAMESPACE + 'import')
        import_el = tree.getroot().find(import_xpath)
        import_el.attrib['schemaLocation'] = iati.resources.resource_filename(iati.resources.get_schema_path('xml', self._get_version()))

        # insert the new element
        tree.getroot().insert(import_el.getparent().index(import_el) + 1, xinclude_el)

        # remove the old element
        etree.strip_elements(tree.getroot(), include_xpath)

        return tree

    def _get_version(self):
        """Return the version that this schema is defined as.

        Returns:
            str or None: The version stated for the schema, according to the value defined in the 'version' attribute at root of the XSD schema. Returns None if there is no 'version' attribute.

        """
        return self._schema_base_tree.getroot().get('version')

    def _flatten_includes(self):
        """For a Schema that contains an xsd:include element, flatten includes so that all nodes are accessible through lxml.

        I.e. Identify the contents of files defined as `<xsd:include schemaLocation="NAME.xsd" />` and bring in the contents.

        Updates:
            self._schema_base_tree: To be the flattened schema. Makes no modification if the schema contains no xsd:include element.

        Todo:
            Add more robust tests for schemas at different versions.

            Consider moving this out of Schema().

            Tidy this up.

        """
        # Ensure that the include element is in a format that can be read by lxml
        tree = self._change_include_to_xinclude(self._schema_base_tree)

        # Adopt the included elements
        if tree is None:
            return
        else:
            tree.xinclude()

        # Find any nested `xsd:schema` elements that exist within the newly flattened schema
        schema_xpath = (iati.constants.NAMESPACE + 'schema')
        for nested_schema_el in tree.getroot().findall(schema_xpath):
            if isinstance(nested_schema_el, etree._Element):  # pylint: disable=protected-access
                # Move contents of nested schema elements up a level
                for elem in nested_schema_el[:]:
                    # Do not duplicate an import statement
                    if 'schemaLocation' in elem.attrib:
                        continue
                    tree.getroot().insert(nested_schema_el.getparent().index(nested_schema_el) + 1, elem)
        # Remove the nested `xsd:schema` elements
        etree.strip_elements(tree.getroot(), schema_xpath)

    def get_xsd_element(self, xsd_element_name):
        """Return an lxml.etree represention for a given xsd:element, based on its name.

        Args:
            xsd_element_name (str): The name of the element to be returned.

        Returns:
            etree._ElementTree / None: The first element tree that matches the element name within the schema. Returns None if no XSD element found.

        Todo:
            Refactor functionality with `get_xsd_attribute` (perhaps to be called `get_xsd_type_by_name`).

        """
        return self._schema_base_tree.find(
            '//xsd:element[@name="{0}"]'.format(xsd_element_name),
            namespaces=iati.constants.NSMAP
        )

    def get_xsd_attribute(self, xsd_attribute_name):
        """Return an lxml.etree represention for a given xsd:attribute, based on its name.

        Args:
            xsd_attribute_name (str): The name of the attribute to be returned.

        Returns:
            etree._ElementTree / None: The first element tree that matches the attribute name within the schema. Returns None if no XSD attribute found.

        Todo:
            Refactor functionality with `get_xsd_element` (perhaps to be called `get_xsd_type_by_name`).

        """
        return self._schema_base_tree.find(
            '//xsd:attribute[@name="{0}"]'.format(xsd_attribute_name),
            namespaces=iati.constants.NSMAP
        )

    def get_child_xsd_element_definitions(self, parent_element):
        """Return a list of child element definitions for a given lxml.etree represention of an xsd:element.

        Args:
            parent_element (etree._ElementTree): The parent represention of an XSD element to find child definitions for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD element definitions that are children to the input element.  If there are no child elements, this will be an empty list.

        Warning:
            At present this is tightly coupled to the iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        """
        child_elements_and_refs = parent_element.findall(
            'xsd:complexType/xsd:sequence/xsd:element',
            namespaces=iati.constants.NSMAP
        )  # This will find all elements defined directly within the schema, or cited by reference.

        # Look for corresponding complexType and add to the child_elements_and_refs
        if parent_element.get('type') is not None:
            child_elements_and_refs += self._schema_base_tree.findall(
                'xsd:complexType[@name="{0}"]/xsd:sequence/xsd:element'.format(parent_element.get('type')),
                namespaces=iati.constants.NSMAP
            )
        return child_elements_and_refs

    def get_child_xsd_elements(self, parent_element):
        """Return a list of child elements for a given lxml.etree represention of an xsd:element.

        Args:
            parent_element (etree._ElementTree): The parent represention of an XSD element to find children for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD elements that are children to the input element.  If there are no child elements, this will be an empty list.

        Warning:
            At present this is tightly coupled to the iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        """
        output = []
        for element_or_ref in self.get_child_xsd_element_definitions(parent_element):
            if element_or_ref.get('ref') is not None:
                # This element is defined via a reference to an xsd:element defined elsewhere in the schema.
                output.append(self.get_xsd_element(element_or_ref.get('ref')))
            elif element_or_ref.get('name') is not None:
                # This element is defined directly within the parent xsd:element.
                output.append(element_or_ref)

        return output

    def get_attributes_definitions_in_xsd_element(self, element):
        """Return a list of attribute defintions that are contained within a given lxml.etree represention of an xsd:element.

        Args:
            element (etree._ElementTree): The lxml represention of an XSD element to find attribute definitions for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD attribute definitions that are contained witin the input element. If there are no attributes, this will be an empty list.

        Warning:
            At present this is tightly coupled to the IATI iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        Todo:
            Test this.

        """
        attributes = element.findall(
            'xsd:complexType/xsd:attribute',
            namespaces=iati.constants.NSMAP
        ) + element.findall(
            'xsd:complexType/xsd:simpleContent/xsd:extension/xsd:attribute',
            namespaces=iati.constants.NSMAP
        )
        if element.get('type') is not None:
            attributes += self._schema_base_tree.findall(
            'xsd:complexType[@name="{0}"]/xsd:simpleContent/xsd:extension/xsd:attribute'.format(element.get('type')),
            namespaces=iati.constants.NSMAP
        )
        return attributes

    def get_attributes_in_xsd_element(self, element):
        """Return a list of attribute elements that are contained within a given lxml.etree represention of an xsd:element.

        Args:
            element (etree._ElementTree): The lxml represention of an XSD element to find attributes for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD attributes that are contained witin the input element. If there are no attributes, this will be an empty list.

        Warning:
            At present this is tightly coupled to the IATI iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.
        """
        output = []
        for attr in self.get_attributes_definitions_in_xsd_element(element):
            if attr.get('ref') is not None and not self.is_attribute_xml_lang(attr):
                output.append(self.get_xsd_attribute(attr.get('ref')))
            else:
                output.append(attr)
        return output

    def is_attribute_xml_lang(self, element):
        """Perform a check on a lxml represention of an xsd:attribute to determine if it is an 'xml:lang' attribute.

        Args:
            element (etree._ElementTree): The lxml represention of the xsd:attribute to check.

        Returns:
            bool: True if the element is an 'xml:lang' attribute, or False if not.

        """
        if element.get('ref') == 'xml:lang':
            return True
        else:
            return False

    def get_xsd_element_or_attribute_name(self, element):
        """Returns the name of a given xsd:element or xsd:attribute element, as defined in the element's @name attribute.

        Args:
            element (etree._ElementTree): The represention of an xsd:element or xsd:attribute element to find the name for.

        Returns:
            str or None: The value within the xsd:element/@name or xsd:attribute/@name. None is returned if no name is found.

        """
        name = element.get('name')

        # Deal with the special case of the 'xml:lang' attributes, which are formally defined in the xml.xsd schema, but the documentation and usage restrictions are set in the IATI schemas.
        if self.is_attribute_xml_lang(element):
            name = 'xml:lang'

        return name

    def _build_xsd_lookup_dict(self):
        """Builds a lookup dictionary containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        Returns:
            dict: Containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        Warning:
            At present this is tightly coupled to the IATI iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        """
        root_element = self.get_xsd_element(self.ROOT_ELEMENT_NAME)
        return self._build_recursive_xsd_lookup_dict(root_element)

    def _build_recursive_xsd_lookup_dict(self, base_element, base_xpath='', output=None):
        """Recursively builds a lookup dictionary containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        Args:
            base_element (etree._ElementTree): The inital element to traverse over.
            base_xpath (str): The XPath for the base_element. Defaults to an empty string.
            output (OrderedDict): An existing output OrderedDict to append results to. Defaults to None, implying that there is no existing output, so a new OrderedDict will be instantiated.

        Returns:
            OrderedDict: Containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        """
        if output is None:
            output = OrderedDict()

        base_element_name = self.get_xsd_element_or_attribute_name(base_element)
        if base_xpath:
            current_xpath = base_xpath + '/' + base_element_name
        else:
            current_xpath = base_element_name
        output[current_xpath] = base_element

        for attribute in self.get_attributes_in_xsd_element(base_element):
            attribute_name = self.get_xsd_element_or_attribute_name(attribute)
            xpath = current_xpath + '/@' + attribute_name
            output[xpath] = attribute

        for child_element in self.get_child_xsd_elements(base_element):
            self._build_recursive_xsd_lookup_dict(child_element, current_xpath, output)

        return output

    def _build_xpath_parent_child_dict(self):
        """Builds a dictionary of parent and child XPaths.

        Returns:
            OrderedDict: Containing an XPath for an element (as keys) and a list of XPaths for all child attributes/elements (as values).
        """
        output = OrderedDict()
        for xpath in self._xsd_lookup.keys():
            xpath_components = xpath.split('/')
            last_component = xpath_components.pop()
            xpath_parent = '/'.join(xpath_components)
            if xpath not in output.keys() and not last_component.startswith('@'):
                output[xpath] = []

            if xpath_parent != '':
                output[xpath_parent].append(xpath)
        return output

    def get_xsd_documentation_string(self, element, language='en', clean_output=True):
        """Return the xsd:documentation string contained within an input XSD element.

        Args:
            element (etree._ElementTree): The element to find documentation within.
            lang (str): The language to find documentation for. Defaults to 'en'.
            clean_output (bool): Define whether to return the raw documentation (i.e. False) or a 'clean' version without unnecessary whitespace (i.e. True). Defaults to True.

        Returns:
            str: The documentation string contained within the input element.

        Todo:
            Find edge cases for this method - for example, where the element references a complex type, but includes documentation within the non-referenced element.

        """
        try:
            documentation = element.xpath(
                'xsd:annotation/xsd:documentation[@xml:lang="{0}"]/text()'.format(language),
                namespaces=iati.constants.NSMAP
            )[0]
        except IndexError:  # Arises when the xpath returns an empty list
            documentation = ''

        if clean_output:
            documentation = ' '.join(documentation.split())
        return documentation

    def get_xsd_input_type_for_element(self, element):
        """Returns the expected XSD data type for a given element.

        Args:
            element (etree._ElementTree): The element to find the type of.

        Returns:
            str: Containing the data type. Will be either 'element' or 'attribute'.

        Todo:
            Consider if further tests are needed.

        """
        try:
            return element.tag.split('}')[-1]
        except AttributeError:
            raise TypeError('Unexpected input type entered.')

    def get_occurances_for_xpath(self, xpath):
        """Returns a dictionary containing the allowed minumum and maximum number of occurances for a given XPath.

        Args:
            xpath (str): The XPath for the element or attribute to find the occurance information for.

        Returns:
            dict: Containing 'min_occurs' and 'max_occurs' (as keys), with the number of allowed occurances (as values). Values are integers or str 'unbounded'.

        Todo:
            Possibly refactor: Could be split into two functions for finding min/max occurs for an element or an attribute.
            Should also split the code to filter for the element/attribute definition into a seperate function.

        """
        # Deal with special case for root elements, which can be defined up to once.
        if xpath == self.ROOT_ELEMENT_NAME:
            return {
                'min_occurs': 0,
                'max_occurs': 1
            }

        element_or_attr = self._xsd_lookup[xpath]
        element_or_attr_name = self.get_xsd_element_or_attribute_name(element_or_attr)
        parent_xpath = self.get_parent_xpath_for_xpath(xpath)
        parent_element = self._xsd_lookup[parent_xpath]

        if self.is_xsd_element_element(element_or_attr):
            element_definitions = self.get_child_xsd_element_definitions(parent_element)
            element = [elem for elem in element_definitions
                if element_or_attr_name in [
                    self.get_xsd_element_or_attribute_name(elem),
                    elem.get('ref')
                ]
            ]  # Filter to return the element definition for the input XPath.
            min_occurs = element[0].get('minOccurs')
            max_occurs = element[0].get('maxOccurs')
        elif self.is_xsd_element_attribute(element_or_attr):
            attr_definitions = self.get_attributes_definitions_in_xsd_element(parent_element)
            attribute = [attr for attr in attr_definitions
                if element_or_attr_name in [
                    self.get_xsd_element_or_attribute_name(attr),
                    attr.get('ref')
                ]
            ]  # Filter to return the attribute definition for the input XPath.
            min_occurs = '1' if attribute[0].get('use') == 'required' else '0'
            max_occurs = '1'  # An attribute can only be used once

        return {
            'min_occurs': int(min_occurs) if min_occurs.isdigit() else min_occurs,
            'max_occurs': int(max_occurs) if max_occurs.isdigit() else max_occurs
        }

    def get_codelist_for_xsd_element(self, element):
        """Returns a list containing allowed codelists for the given element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

    def get_rules_for_xsd_element(self, element):
        """Returns a list containing rules objects for the given element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

    def get_guidance_for_xsd_element(self, element):
        """Returns guidance for the given element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

    def get_parent_xpath_for_xpath(self, xpath):
        """Returns an XPath refering to the parent element for the element/attribute at the given input XPath.

        Args:
            xpath (str): The XPath to find the parent for.

        Returns:
            str or None: An XPath relating to the parent element for the input XPath. Returns None if there is no parent element.

        Raises:
            ValueError: If the input XPath is not a valid XPath for this Schema.

        """
        if xpath not in self._xsd_lookup.keys():
            raise ValueError('The input XPath is not a valid XPath for this Schema.')

        for parent_xpath, child_xpaths in self._xpath_lookup.items():
            if xpath in child_xpaths:
                return parent_xpath

        return None  # The input XPath was not found in any of the child XPaths.

    def get_xpaths_for_sibling_types(self, xpath, same_type=False):
        """Returns a list of XPaths that refer to elements that are at the same level as the input XPath.

        Args:
            xpath (str): An XPath representing an XSD element or attribute to find the siblings for.
            same_type (bool): If set to True, this ensures that only sibling elements of the same data type will be returned. Defaults to True.

        Returns:
            list: Containing XPaths for the elements/attributes that are at the same level in this Schema.

        """
        parent_xpath = self.get_parent_xpath_for_xpath(xpath)
        if parent_xpath is None:
            sibling_xpaths = []  # parent_xpath will be None where we are looking for the parent of the root element.
        else:
            sibling_xpaths = self.get_xpaths_for_child_types(parent_xpath)
            sibling_xpaths.remove(xpath)  # Remove the input XPath from child types

        element = self._xsd_lookup[xpath]
        if same_type and self.is_xsd_element_attribute(element):
            sibling_xpaths = [path for path in sibling_xpaths if self.is_xsd_element_attribute(self._xsd_lookup[path])]

        if same_type and self.is_xsd_element_element(element):
            sibling_xpaths = [path for path in sibling_xpaths if self.is_xsd_element_element(self._xsd_lookup[path])]

        return sibling_xpaths

    def get_xpaths_for_child_types(self, xpath):
        """Returns a list of XPaths for elements/attributes that are children of the element at the input XPath.

        Args:
            xpath (str): The XPath refering to an element or attribute within this Schema.

        Returns:
            list of str / None: List containing XPaths that refer to child elements. None if the input XPath is an attribute.

        Raises:
            ValueError: If the input XPath is not a valid XPath for this Schema.

        """
        if xpath not in self._xsd_lookup.keys():
            raise ValueError('The input XPath is not a valid XPath for this Schema.')

        try:
            return copy(self._xpath_lookup[xpath])
        except KeyError:
            return None

    def get_xpaths_for_xsd_element_attributes(self, element):
        """Returns a list of XPaths for attributes contained within the given element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

    def get_documentation_for_xpath(self, xpath):
        """Returns a dictionary containing full documentation for the given XPath.

        Args:
            xpath (str): An XPath representing an XSD element or attribute to return documentation for.

        Returns:
            dict: Containing documentation on for the input XPath.

        Raises:
            ValueError: If the input XPath is not found within this Schema.

        Todo:
            Add more robust tests.

        """
        try:
            element = self._xsd_lookup[xpath]
        except KeyError:
            raise ValueError('The input xpath ({0}) is not valid for this schema.'.format(xpath))

        return {
            'documentation': self.get_xsd_documentation_string(element),
            'input_type': self.get_xsd_input_type_for_element(element),
            'occurances': self.get_occurances_for_xpath(xpath),
            'parent_xpath': self.get_parent_xpath_for_xpath(xpath),
            'sibling_xpaths': self.get_xpaths_for_sibling_types(xpath),
            'child_xpaths': self.get_xpaths_for_child_types(xpath)
        }

    def is_this_an_xsd_element(self, element):
        """Raise error if not an XML schema element.

        Returns:
            str: An expected value of a given XML schema element.

        Raises:
            TypeError: When given an argument of a non-permitted type.
            ValueError: When given an XML element that is not a valid schema element.

        """
        expected_values = ['attribute', 'element']
        element_type = self.get_xsd_input_type_for_element(element)
        if element_type not in expected_values:
            raise ValueError('Got {0} but expected {1}'.format(element_type, ' or '.join(expected_values)))

        return element_type

    def is_xsd_element_attribute(self, element):
        """Check whether given element is an attribute.

        Returns:
            bool: Changes depending on whether a given element is an attribute.

        Raises:
            TypeError: When given an argument of a non-permitted type.
            ValueError: When given an XML element that is not a valid schema element.

        """
        element_type = self.is_this_an_xsd_element(element)

        return element_type == 'attribute'

    def is_xsd_element_element(self, element):
        """Check whether given element is an attribute.

        Returns:
            bool: Changes depending on whether a given element is an attribute.

        Raises:
            TypeError: When given an argument of a non-permitted type.

        """
        element_type = self.is_this_an_xsd_element(element)

        return element_type == 'element'

    def validator(self):
        """Return a schema that can be used for validation.

        Takes the base schema and converts it into an object that lxml can deal with.

        Returns:
            etree.XMLSchema: A schema that can be used for validation.

        Raises:
            iati.exceptions.SchemaError: An error occurred in the creation of the validator.

        """
        try:
            return iati.utilities.convert_tree_to_schema(self._schema_base_tree)
        except etree.XMLSchemaParseError as err:
            iati.utilities.log_error(err)
            raise iati.exceptions.SchemaError('Problem parsing Schema')


class ActivitySchema(Schema):
    """Representation of an IATI Activity Schema as defined within the IATI SSOT."""

    ROOT_ELEMENT_NAME = 'iati-activities'


class OrganisationSchema(Schema):
    """Representation of an IATI Organisation Schema as defined within the IATI SSOT."""

    ROOT_ELEMENT_NAME = 'iati-organisations'
