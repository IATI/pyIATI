"""A module containing a core representation of IATI Schemas."""
from lxml import etree
import iati.core.exceptions
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT.

    Attributes:
        name (str): The name of the Schema.
        schema (etree.XMLSchema): An actual Schema that can be used for validation.
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
        """
        self.name = name
        self.schema = None
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
                generated_schema = iati.core.utilities.convert_tree_to_schema(loaded_tree)
                if isinstance(generated_schema, etree.XMLSchema):
                    self.schema = generated_schema
