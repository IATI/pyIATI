"""A module containing a core representation of IATI Schemas."""
from lxml import etree
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT."""

    def __init__(self, name=None):
        """Initialise a Schema."""
        # TODO: Better determine how to load from XSD
        self.name = name
        self.schema = None

        if name:
            # TODO: Use try-except pattern
            path = iati.core.resources.path_schema(self.name)
            try:
                loaded_tree = iati.core.resources.load_as_tree(path)
            except OSError:
                iati.core.utilities.log_error("Failed to load tree at {0}".format(path))
            else:
                generated_schema = iati.core.utilities.convert_to_schema(loaded_tree)
                if isinstance(generated_schema, etree.XMLSchema):
                    self.schema = generated_schema
