"""
A module containing tests for the library implementation of accessing resources.
"""
from lxml import etree
import iati.core.resources


class TestResources(object):
    """A container for tests relating to resources"""

    def test_codelist_flow_type(self):
        """Check that the FlowType codelist contains content"""
        path = iati.core.resources.path_codelist('FlowType')

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 3200

    def test_resource_filename(self):
        """Check that resource filenames are found correctly"""
        path = iati.core.resources.BASE_PATH_SCHEMAS
        filename = iati.core.resources.resource_filename(path)

        assert len(filename) > len(path)
        assert filename.endswith(path)

    def test_schema_activity_string(self):
        """Check that the Activity schema file contains content"""
        path = iati.core.resources.path_schema('iati-activities-schema')

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 130000

    def test_schema_activity_schema(self):
        """Check that the Activity schema loads into a Schema

        This additionally involves checking that imported schemas also work.
        """
        schema = iati.core.resources.load_as_schema('iati-activities-schema')

        assert isinstance(schema, etree.XMLSchema)

    def test_schema_activity_tree(self):
        """Check that the Activity schema loads into an XML Tree

        This additionally involves checking that imported schemas also work.
        """
        path = iati.core.resources.path_schema('iati-activities-schema')
        schema = iati.core.resources.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)
