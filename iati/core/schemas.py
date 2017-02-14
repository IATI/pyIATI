"""A module containing a core representation of IATI Schemas."""
import copy
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

    Todo:
        Create a custom dictionary type that prevents overwriting values and only allows the correct types to be added.
    """

    def __init__(self, name=None):
        """Initialise a Schema.

        Args:
            name (str): The name of the schema being initialised.
                This name refers to a file contained within the core IATI resources folder.

        Raises:
            iati.core.exceptions.SchemaError: An error occurred during the creation of the Schema.

        Todo:
            Allow for generation of schemas outside the IATI SSOT.

            Better use the try-except pattern.

            Allow the base schema to be modified after initialisation.
        """
        self.name = name
        self._schema_base_tree = None
        self.codelists = set()

        if name:
            path = iati.core.resources.path_schema(self.name)
            try:
                loaded_tree = iati.core.resources.load_as_tree(path)
            except (IOError, OSError):
                msg = "Failed to load tree at '{0}' when creating Schema.".format(path)
                iati.core.utilities.log_error(msg)
                raise iati.core.exceptions.SchemaError
            else:
                self._schema_base_tree = loaded_tree

    def validator(self):
        """A schema that can be used for validation.

        Takes the base schema and dynamically injects elements for content checking.

        Returns:
            etree.XMLSchema: A schema that can be used for validation.

        Todo:
            Implement Codelist content checking.

            Implement Ruleset content checking.

            Add configuration parameters.

            Make the algorithm relating to mappings not-hideous.
        """
        # tree = copy.deepcopy(self._schema_base_tree)
        tree = self._schema_base_tree

        if len(self.codelists):
            mappings = iati.core.codelists.fetch_mappings()
            updated_xpaths = {}

            for xpath, (ref, _) in mappings.items():
                # the XPaths are for a data file rather than a Schema, so need formatting differently
                path_sections = xpath.split('/')
                try:
                    elements = path_sections[path_sections.index('iati-activity') + 1:-1]
                    # locate the relevant elements
                    xpath_sections = ['{http://www.w3.org/2001/XMLSchema}element[@name="' + el + '"]' for el in elements]
                    # locate the attribute on the final element
                    xpath_sections.append('{http://www.w3.org/2001/XMLSchema}attribute[@name="' + path_sections[-1:][0][1:] + '"]')

                    updated_xpaths[ref] = '//'.join(xpath_sections)
                except ValueError:
                    pass

            for codelist in self.codelists:
                if codelist.name in updated_xpaths:
                    thing_to_update = tree.getroot().find(updated_xpaths[codelist.name])
                    thing_to_update.attrib['type'] = codelist.name + '-type'
                tree.getroot().append(codelist.xsd_tree())

            try:
                a = iati.core.utilities.convert_tree_to_schema(tree)
                return a
            except etree.XMLSchemaParseError as err:
                iati.core.utilities.log_error(err)
        else:
            return iati.core.utilities.convert_tree_to_schema(tree)
