"""A module containing tests for the library implementation of accessing resources."""
from lxml import etree
import pytest
import iati.core.resources


class TestResources(object):
    """A container for tests relating to resources"""

    def test_codelist_flow_type(self):
        """Check that the FlowType codelist contains content"""
        path = iati.core.resources.path_codelist('FlowType')

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 3200

    def test_find_codelist_paths(self):
        """Check that all codelist paths are being found.

        Todo:
            Add other tests relating to specific versions of the Standard.
        """
        paths = iati.core.resources.find_all_codelist_paths()

        assert len(paths) == 62
        for path in paths:
            assert path[-4:] == iati.core.resources.FILE_CODELIST_EXTENSION
            assert iati.core.resources.BASE_PATH_CODELISTS in path

    def test_find_schema_paths(self):
        """Check that all schema paths are being found.

        Todo:
            Add other tests relating to specific versions of the Standard.

            Handle all paths to schemas being found correctly.
        """
        paths = iati.core.resources.find_all_schema_paths()

        assert len(paths) == 1
        for path in paths:
            assert path[-4:] == iati.core.resources.FILE_SCHEMA_EXTENSION
            assert iati.core.resources.BASE_PATH_SCHEMAS_202 in path

    @pytest.mark.parametrize('name,location', [
        ('Name', None),
        ('Name', 'embedded'),
        ('Name', 'non-embedded'),
        ('Name.xml', None),
        ('Name.xml', 'embedded'),
        ('Name.xml', 'non-embedded'),
    ])
    def test_path_codelist_name(self, name, location):
        """Check that a codelist path is found from just a name.

        Todo:
            Tidy up if-else mess.
        """
        if location is None:
            path = iati.core.resources.path_codelist(name)
        else:
            path = iati.core.resources.path_codelist(name, location)

        assert path[-4:] == '.xml'
        assert path.count('.xml') == 1
        if location == 'embedded':
            assert iati.core.resources.BASE_PATH_CODELISTS_EMBEDDED in path
        else:
            assert iati.core.resources.BASE_PATH_CODELISTS_NON_EMBEDDED in path

    @pytest.mark.parametrize('name,location', [
        ('Name', 23487),
        ('Name', 'invalid type')
    ])
    def test_path_codelist_invalid_type(self, name, location):
        """Check that an error is raised when attempting to find a codelist of invalid type."""
        try:
            _ = iati.core.resources.path_codelist(name, location)
        except ValueError:
            assert True
        else:
            # a ValueError should be raised, meaning this is not reached
            assert False

    def test_resource_filename(self):
        """Check that resource file names are found correctly

        Todo:
            Implement better assertions.
        """
        path = iati.core.resources.BASE_PATH_SCHEMAS
        filename = iati.core.resources.resource_filename(path)

        assert len(filename) > len(path)
        assert filename.endswith(path)

    def test_schema_activity_string(self):
        """Check that the Activity schema file contains content"""
        path = iati.core.resources.path_schema('iati-activities-schema')

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 130000

    def test_schema_activity_tree(self):
        """Check that the Activity schema loads into an XML Tree

        This additionally involves checking that imported schemas also work.
        """
        path = iati.core.resources.path_schema('iati-activities-schema')
        schema = iati.core.resources.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)  # pylint: disable=protected-access
