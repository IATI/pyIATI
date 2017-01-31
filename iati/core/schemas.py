"""A module containing a core representation of IATI Schemas."""
from lxml import etree
import iati.core.resources


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT."""

    def __init__(self, name=None):
        # TODO: Better determine how to load from XSD
        self.name = name
        self.schema = None

        if name:
            generated_schema = iati.core.resources.load_as_schema(self.name)
            if isinstance(generated_schema, etree.XMLSchema):
                self.schema = generated_schema
