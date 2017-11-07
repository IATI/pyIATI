"""A module containing a core representation of IATI Schemas."""
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

    def flatten_includes(self, tree):
        """Flatten includes so that all nodes are accessible through lxml.

        Identify the contents of files defined as `<xsd:include schemaLocation="NAME.xsd" />` and bring in the contents.

        Args:
            tree (etree._ElementTree): The tree to flatten.

        Returns:
            etree._ElementTree: The flattened tree.

        Todo:
            Add more robust tests for schemas at different versions.

            Consider moving this out of Schema().

            Tidy this up.

        """
        # change the include to a format that lxml can read
        tree = self._change_include_to_xinclude(tree)

        # adopt the included elements
        tree.xinclude()

        # remove nested schema elements
        schema_xpath = (iati.constants.NAMESPACE + 'schema')
        for nested_schema_el in tree.getroot().findall(schema_xpath):
            if isinstance(nested_schema_el, etree._Element):  # pylint: disable=protected-access
                # move contents of nested schema elements up a level
                for elem in nested_schema_el[:]:
                    # do not duplicate an import statement
                    if 'schemaLocation' in elem.attrib:
                        continue
                    tree.getroot().insert(nested_schema_el.getparent().index(nested_schema_el) + 1, elem)
        # remove the nested schema elements
        etree.strip_elements(tree.getroot(), schema_xpath)

        return tree

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
