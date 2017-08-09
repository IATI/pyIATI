"""A module containing a core representation of IATI Schemas."""
from collections import OrderedDict
from lxml import etree
import iati.core.codelists
import iati.core.constants
import iati.core.exceptions
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT.

    Attributes:
        codelists (set): The Codelists asspciated with this Schema. This is a read-only attribute.
        root_element_name (str): The name of the root element within the schema - i.e. 'iati-activities' for the activity schema and 'iati-organisations' for the organisation schema.

    Warning:
        The private attribute allowing access to the base Schema Tree is likely to change in determining a good way of accessing the contained schema content.

    Todo:
        Determine a good API for accessing the XMLSchema that the iati.core.Schema represents.

        Determine how to distinguish and handle the different types of Schema - activity, organisation, codelist, other.

    """

    root_element_name = ''

    def __init__(self, path):
        """Initialise a Schema.

        Args:
            path (str): The path to the schema that is being initialised.

        Raises:
            iati.core.exceptions.SchemaError: An error occurred during the creation of the Schema.

        Warning:
            The format of the constructor is likely to change. It needs to be less reliant on the name acting as a UID, and allow for other attributes to be provided at this point.

            The raised exceptions are likely to change upon review of IATI-specific exceptions.

            Need to define a good API for accessing public and private attributes. Requiring something along the lines of `schema.schema` is likely not ideal. An improved understanding of use cases will be required for this.

        Todo:
            Allow for generation of schemas outside the IATI SSOT.

            Better use the try-except pattern.

            Allow the base schema to be modified after initialisation.

            Create test instance where the SchemaError is raised.

        """
        self._schema_base_tree = None
        self.codelists = set()

        try:
            loaded_tree = iati.core.resources.load_as_tree(path)
        except (IOError, OSError):
            msg = "Failed to load tree at '{0}' when creating Schema.".format(path)
            iati.core.utilities.log_error(msg)
            raise iati.core.exceptions.SchemaError
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

        Params:
            tree (etree._ElementTree): The tree within which xsd:include is to be changed to xi:include.

        Returns:
            etree._ElementTree: The modified tree.

        Todo:
            Make resource locations more able to handle the general case.

            Consider moving this out of Schema().

            Tidy this up.

            Consider using XSLT.

        """
        # identify the old info
        include_xpath = (iati.core.constants.NAMESPACE + 'include')
        include_el = tree.getroot().find(include_xpath)
        if include_el is None:
            return
        include_location = include_el.attrib['schemaLocation']

        # add namespace for XInclude
        xi_name = 'xi'
        xi_uri = 'http://www.w3.org/2001/XInclude'
        iati.core.utilities.add_namespace(tree, xi_name, xi_uri)
        new_nsmap = {}
        for key, value in iati.core.constants.NSMAP.items():
            new_nsmap[key] = value
        new_nsmap[xi_name] = xi_uri

        # create a new element
        xinclude_el = etree.Element(
            '{' + xi_uri + '}include',
            href=iati.core.resources.resource_filename(iati.core.resources.get_schema_path(include_location[:-4])),
            parse='xml',
            nsmap=new_nsmap
        )

        # make the path to `xml.xsd` reference the correct file
        import_xpath = (iati.core.constants.NAMESPACE + 'import')
        import_el = tree.getroot().find(import_xpath)
        import_el.attrib['schemaLocation'] = iati.core.resources.resource_filename(iati.core.resources.get_schema_path('xml'))

        # insert the new element
        tree.getroot().insert(import_el.getparent().index(import_el) + 1, xinclude_el)

        # remove the old element
        etree.strip_elements(tree.getroot(), include_xpath)

        return tree

    def _flatten_includes(self):
        """For a Schema that contains an xsd:include element, flatten includes so that all nodes are accessible through lxml.

        I.e. Identify the contents of files defined as `<xsd:include schemaLocation="NAME.xsd" />` and bring in the contents.

        Updates:
            self._schema_base_tree: To be the flattened schema. Makes no modification if the schema contains no xsd:include element.

        Todo:
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
        schema_xpath = (iati.core.constants.NAMESPACE + 'schema')
        for nested_schema_el in tree.getroot().findall(schema_xpath):
            if isinstance(nested_schema_el, etree._Element):
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
            namespaces=iati.core.constants.NSMAP
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
            namespaces=iati.core.constants.NSMAP
        )

    def get_child_xsd_elements(self, parent_element):
        """Return a list of child elements for a given lxml.etree represention of an xsd:element.

        Args:
            parent_element (etree._ElementTree): The parent represention of an XSD element to find children for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD elements that are children to the input element.  If there are no child elements, this will be an empty list.

        Warning:
            At present this is tightly coupled to the iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        """
        child_elements_and_refs = parent_element.findall(
            'xsd:complexType/xsd:sequence/xsd:element',
            namespaces=iati.core.constants.NSMAP
        )  # This will find all elements defined directly within the schema, or cited by reference.

        # Look for corresponding complexType and add to the child_elements_and_refs
        if parent_element.get('type') is not None:
            complexType_children = self._schema_base_tree.findall(
                'xsd:complexType[@name="{0}"]/xsd:sequence/xsd:element'.format(parent_element.get('type')),
                namespaces=iati.core.constants.NSMAP
            )
            child_elements_and_refs = child_elements_and_refs + complexType_children

        output = []
        for element_or_ref in child_elements_and_refs:
            if element_or_ref.get('ref') is not None:
                # This element is defined via a reference to an xsd:element defined elsewhere in the schema.
                output.append(self.get_xsd_element(element_or_ref.get('ref')))
            elif element_or_ref.get('name') is not None:
                # This element is defined directly within the parent xsd:element.
                output.append(element_or_ref)

        return output

    def get_attributes_in_xsd_element(self, element):
        """Return a list of attribute elements that are contained within a given lxml.etree represention of an xsd:element.

        Args:
            element (etree._ElementTree): The lxml represention of an XSD element to find attributes for.

        Returns:
            list of etree._ElementTree: A list containing representions of XSD attributes that are contained witin the input element. If there are no attributes, this will be an empty list.

        Warning:
            At present this is tightly coupled to the IATI iati-activities-schema, iati-organisations-schema and iati-common schemas. The behaviour for other types of schema is undefined.

        Todo:
            Possibly refactor.

        """
        attributes = element.findall(
            'xsd:complexType/xsd:attribute',
            namespaces=iati.core.constants.NSMAP
        ) + element.findall(
            'xsd:complexType/xsd:simpleContent/xsd:extension/xsd:attribute',
            namespaces=iati.core.constants.NSMAP
        )
        if element.get('type') is not None:
            attributes += self._schema_base_tree.findall(
            'xsd:complexType[@name="{0}"]/xsd:simpleContent/xsd:extension/xsd:attribute'.format(element.get('type')),
            namespaces=iati.core.constants.NSMAP
        )
        output = []
        for attr in attributes:
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
        root_element = self.get_xsd_element(self.root_element_name)
        return self._build_recursive_xsd_lookup_dict(root_element)

    def _build_recursive_xsd_lookup_dict(self, base_element, base_xpath='', output=None):
        """Recursively builds a lookup dictionary containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        Args:
            base_element (etree._ElementTree): The inital element to traverse over.
            base_xpath (str): The XPath for the base_element. Defaults to an empty string.
            output (OrderedDict): An existing output OrderedDict to append results to. Defaults to None, implying that there is no existing output, so a new OrderedDict will be instantiated.

        Returns:
            OrderedDict: Containing an XPath (as keys) with the corresponding lxml represention of the xsd:element or xsd:attribute (as values).

        Todo:
            Rename to an internal method.

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
                namespaces=iati.core.constants.NSMAP
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

    def get_occurances_for_xsd_element(self, element):
        """Returns a dictionary containing the allowed minumum and maximum number of occurances for a given element.

        The function awaits implementation of `get_xsd_parent_element`, as the defined minumum and maximum number of occurances is defined in the parent element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

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

    def get_xsd_sibling_elements(self, element):
        """Returns a list of XPaths for sibling elements to the given input element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

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
            return self._xpath_lookup[xpath]
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

    def get_full_documentation_for_xsd_element(self, element):
        """Returns a dictionary containing documentation information for the given element.

        Warning:
            It is likely that the input param will change from `element` to `xpath`.

            The name of this method may change, depending on work on the components of this.

        Todo:
            Add tests.

            Implement functionality.

        """
        raise NotImplementedError

    def get_documentation_for_xpath(self, xpath):
        """Returns a dictionary containing documentation for the given XPath.

        Warning:
            The name of this method may change, depending on work on the components of this.

        Todo:
            Add tests.

            Implement functionality.

        """
        # This will be the main user API. Will involve something like:
        # try:
        #     element = self._xsd_lookup[xpath]
        # except IndexError:
        #     raise Exception
        # return self.get_full_documentation_for_xsd_element(element)
        raise NotImplementedError

    def is_xsd_element_attribute(self, element):
        """Check whether given element is an attribute.

        Returns:
            bool: Changes depending on whether a given element is an attribute.

        Raises:
            TypeError: When given an argument of a non-permitted type.

        """
        try:
            element_type = element.tag.split('}')[-1]
            if element_type not in ['attribute', 'element']:
                raise ValueError
        except AttributeError:
            raise TypeError

        return element_type == 'attribute'


class ActivitySchema(Schema):
    """Represenation of an IATI Activity Schema as defined within the IATI SSOT."""

    root_element_name = 'iati-activities'


class OrganisationSchema(Schema):
    """Represenation of an IATI Organisation Schema as defined within the IATI SSOT."""

    root_element_name = 'iati-organisations'
