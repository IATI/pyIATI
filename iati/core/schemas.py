"""A module containing a core representation of IATI Schemas."""
from lxml import etree
import iati.core.codelists
import iati.core.exceptions
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT.

    Attributes:
        name (str): The name of the Schema.
        codelists (set): The Codelists asspciated with this Schema. This is a read-only attribute.

    Warning:
        The private attribute allowing access to the base Schema Tree is likely to change in determining a good way of accessing the contained schema content.

    Todo:
        Determine a good API for accessing the XMLSchema that the iati.core.schemas.Schema represents.

        Determine how to distinguish and handle the different types of Schema - activity, organisation, codelist, other.
    """

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
            path = iati.core.resources.path_schema(self.name)
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

    def validator(self):
        """A schema that can be used for validation.

        Takes the base schema and dynamically injects elements for content checking.
        Returns:
            etree.XMLSchema: A schema that can be used for validation.
        Todo:
            Implement Codelist content checking.
            Implement Ruleset content checking.
            Add configuration parameters.
        """
        # tree = copy.deepcopy(self._schema_base_tree)
        tree = self._schema_base_tree

        if len(self.codelists):
            for codelist in self.codelists:
                if codelist.name == 'Version':
                    xpath = ('{http://www.w3.org/2001/XMLSchema}element[@name="' + 'iati-activities' + '"]//{http://www.w3.org/2001/XMLSchema}attribute[@name="version"]')
                else:  # TODO: elif
                    xpath = ('{http://www.w3.org/2001/XMLSchema}element[@name="' + 'sector' + '"]//{http://www.w3.org/2001/XMLSchema}attribute[@name="code"]')

                el_to_update = tree.getroot().find(xpath)
                el_to_update.attrib['type'] = codelist.name + '-type'

                tree.getroot().append(codelist.xsd_tree())

            try:
                return iati.core.utilities.convert_tree_to_schema(tree)
            except etree.XMLSchemaParseError as err:
                iati.core.utilities.log_error(err)
        else:
            return iati.core.utilities.convert_tree_to_schema(tree)
