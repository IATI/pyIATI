"""A module containing a core representation of IATI Schemas."""
from lxml import etree
import iati.core.codelists
import iati.core.constants
import iati.core.exceptions
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT.

    Attributes:
        name (str): The name of the Schema.
        codelists (set): The Codelists asspciated with this Schema. This is a read-only attribute.
        root_element_name (str): The name of the root element within the schema - i.e. 'iati-activities' for the activity schema and 'iati-organisations' for the organisation schema.

    Warning:
        The private attribute allowing access to the base Schema Tree is likely to change in determining a good way of accessing the contained schema content.

    Todo:
        Determine a good API for accessing the XMLSchema that the iati.core.ActivitySchema represents.

        Determine how to distinguish and handle the different types of Schema - activity, organisation, codelist, other.

    """
    root_element_name = ''

    def __init__(self, name=None):
        """Initialise a Schema.

        Args:
            name (str): The name of the schema being initialised.
                This name refers to a file contained within the core IATI resources folder.

        Raises:
            TypeError: The type of the provided name is incorrect.
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
        self.name = name
        self._schema_base_tree = None
        self.codelists = set()

        if isinstance(name, str):
            path = iati.core.resources.get_schema_path(self.name)
            try:
                loaded_tree = iati.core.resources.load_as_tree(path)
            except (IOError, OSError):
                msg = "Failed to load tree at '{0}' when creating Schema.".format(path)
                iati.core.utilities.log_error(msg)
                raise iati.core.exceptions.SchemaError
            else:
                self._schema_base_tree = loaded_tree
        elif name is not None:
            msg = "The name of the Schema is an invalid type. Must be a string, though was a {0}.".format(type(name))
            iati.core.utilities.log_error(msg)
            raise TypeError(msg)

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
            Check whether this is safe in the general case, so allowing it to be performed in __init__().

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

    def flatten_includes(self, tree):
        """Flatten includes so that all nodes are accessible through lxml.

        Identify the contents of files defined as `<xsd:include schemaLocation="NAME.xsd" />` and bring in the contents.

        Params:
            tree (etree._ElementTree): The tree to flatten.

        Returns:
            etree._ElementTree: The flattened tree.

        Todo:
            Consider moving this out of Schema().

            Tidy this up.

        """
        # change the include to a format that lxml can read
        tree = self._change_include_to_xinclude(tree)

        # adopt the included elements
        tree.xinclude()

        # remove nested schema elements
        schema_xpath = (iati.core.constants.NAMESPACE + 'schema')
        for nested_schema_el in tree.getroot().findall(schema_xpath):
            if isinstance(nested_schema_el, etree._Element):
                # move contents of nested schema elements up a level
                for elem in nested_schema_el[:]:
                    # do not duplicate an import statement
                    if 'schemaLocation' in elem.attrib:
                        continue
                    tree.getroot().insert(nested_schema_el.getparent().index(nested_schema_el) + 1, elem)
        # remove the nested schema elements
        etree.strip_elements(tree.getroot(), schema_xpath)

        return tree


class ActivitySchema(Schema):
    root_element_name = 'iati-activities'
    pass


class OrganisationSchema(Schema):
    root_element_name = 'iati-organisations'
    pass
