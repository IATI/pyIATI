"""A module containing tests for the library implementation of accessing resources."""
from lxml import etree
import pytest
import iati.core.resources


class TestResources(object):
    """A container for tests relating to resources."""

    @pytest.mark.parametrize('version, expected_version_foldername', [
        ('2.02', '202')
    ])
    def test_get_folder_name_for_version(self, version, expected_version_foldername):
        """Check that expected components are present within folder paths."""
        path = iati.core.resources.get_folder_name_for_version(version)
        assert expected_version_foldername == path

    @pytest.mark.parametrize('version', [
        '1.00',
        '1',
        1,
        1.01,  # A verion must be specified as a string
        'string'
    ])
    def test_get_folder_name_for_version_invalid_version(self, version):
        """Check that an invalid version of the Standard raises a ValueError exception."""
        with pytest.raises(ValueError):
            iati.core.resources.get_folder_name_for_version(version)

    @pytest.mark.parametrize('version', [
        '2.02',
    ])
    @pytest.mark.parametrize('path_component', [
        'resources',
        'standard'
    ])
    def test_get_folder_path_for_version(self, version, path_component):
        """Check that expected components are present within folder paths."""
        path = iati.core.resources.get_folder_path_for_version(version)
        assert path_component in path

    def test_codelist_flow_type(self):
        """Check that the FlowType codelist contains content."""
        path = iati.core.resources.get_codelist_path('FlowType')

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
            assert iati.core.resources.PATH_CODELISTS in path

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

    @pytest.mark.parametrize('codelist', [
        'Name',
        'Name.xml',
    ])
    def test_get_codelist_path_name(self, codelist):
        """Check that a codelist path is found from just a name."""
        path = iati.core.resources.get_codelist_path(codelist)

        assert path[-4:] == iati.core.resources.FILE_CODELIST_EXTENSION
        assert path.count(iati.core.resources.FILE_CODELIST_EXTENSION) == 1
        assert iati.core.resources.PATH_CODELISTS in path

    def test_resource_filename(self):
        """Check that resource file names are found correctly.

        Todo:
            Implement better assertions.

        """
        path = iati.core.resources.PATH_SCHEMAS
        filename = iati.core.resources.resource_filename(path)

        assert len(filename) > len(path)
        assert filename.endswith(path)

    def test_schema_activity_string(self):
        """Check that the Activity schema file contains content."""
        path = iati.core.resources.get_schema_path('iati-activities-schema')

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 130000

    def test_schema_activity_tree(self):
        """Check that the Activity schema loads into an XML Tree.

        This additionally involves checking that imported schemas also work.

        """
        path = iati.core.resources.get_schema_path('iati-activities-schema')
        schema = iati.core.resources.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)  # pylint: disable=protected-access
