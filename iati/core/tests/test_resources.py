"""A module containing tests for the library implementation of accessing resources."""
from lxml import etree
import pytest
import six
import iati.core.constants
import iati.core.resources


class TestResources(object):
    """A container for tests relating to resources."""

    @pytest.mark.parametrize('version, expected_version_foldername', [
        ('2.02', '202'),
        ('2.01', '201'),
        ('1.05', '105'),
        ('1.04', '104')
    ])
    def test_get_folder_name_for_version(self, version, expected_version_foldername):
        """Check that expected components are present within folder paths."""
        path = iati.core.resources.get_folder_name_for_version(version)
        assert expected_version_foldername == path

    @pytest.mark.parametrize('version', [
        '1.00',
        '1',
        1,
        1.01,  # A version must be specified as a string
        'string'
    ])
    def test_get_folder_name_for_version_invalid_version(self, version):
        """Check that an invalid version of the Standard raises a ValueError exception."""
        with pytest.raises(ValueError):
            iati.core.resources.get_folder_name_for_version(version)

    @pytest.mark.parametrize('path_component', [
        'resources',
        'standard'
    ])
    def test_get_folder_path_for_version(self, standard_version_optional, path_component):
        """Check that expected components are present within folder paths."""
        path = iati.core.resources.get_folder_path_for_version(*standard_version_optional)
        assert path_component in path

    def test_codelist_flow_type(self, standard_version_optional):
        """Check that the FlowType codelist is loaded as a string and contains content."""
        path = iati.core.resources.get_codelist_path('FlowType', *standard_version_optional)

        content = iati.core.resources.load_as_string(path)

        assert len(content) > 3200

    def test_find_codelist_paths(self, codelist_lengths_by_version):
        """Check that all codelist paths are being found."""
        paths = iati.core.resources.get_all_codelist_paths(codelist_lengths_by_version[0])

        assert len(paths) == codelist_lengths_by_version[1]
        for path in paths:
            assert path[-4:] == iati.core.resources.FILE_CODELIST_EXTENSION
            assert iati.core.resources.PATH_CODELISTS in path

    def test_get_all_activity_schema_paths(self, standard_version_optional):
        """Check that all activity schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        activity_paths = iati.core.resources.get_all_activity_schema_paths(*standard_version_optional)

        assert len(activity_paths) == 1

    def test_get_all_organisation_schema_paths(self, standard_version_optional):
        """Check that all organisation schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        organisation_paths = iati.core.resources.get_all_organisation_schema_paths(*standard_version_optional)

        assert len(organisation_paths) == 1

    def test_find_schema_paths(self, standard_version_optional):
        """Check that both the activity and organisation schema paths are being found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        paths = iati.core.resources.get_all_schema_paths(*standard_version_optional)

        assert len(paths) == 2

    @pytest.mark.parametrize('get_schema_path_function', [
        iati.core.resources.get_all_schema_paths,
        iati.core.resources.get_all_activity_schema_paths,
        iati.core.resources.get_all_organisation_schema_paths
    ])
    def test_find_schema_paths_file_extension(self, standard_version_optional, get_schema_path_function):
        """Check that the correct file extension is present within file paths returned by get_all_*schema_paths functions."""
        paths = get_schema_path_function(*standard_version_optional)

        for path in paths:
            assert path[-4:] == iati.core.resources.FILE_SCHEMA_EXTENSION

    def test_get_test_data_paths_in_folder(self):
        """Check that test data is being found in specified subfolders."""
        paths = iati.core.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail')

        assert len(paths) == 237

    @pytest.mark.parametrize('codelist', [
        'Name',
        'Name.xml',
    ])
    def test_get_codelist_path_name(self, standard_version_optional, codelist):
        """Check that a codelist path is found from just a name."""
        path = iati.core.resources.get_codelist_path(codelist, *standard_version_optional)

        assert path[-4:] == iati.core.resources.FILE_CODELIST_EXTENSION
        assert path.count(iati.core.resources.FILE_CODELIST_EXTENSION) == 1
        assert iati.core.resources.PATH_CODELISTS in path

    def test_load_as_bytes(self):
        """Test that resources.load_as_bytes returns a bytes object with the expected content."""
        path_test_data = iati.core.resources.get_test_data_path('invalid')

        result = iati.core.resources.load_as_bytes(path_test_data)

        assert isinstance(result, bytes)
        assert result == 'This is a string that is not valid XML\n'.encode()

    def test_load_as_dataset(self):
        """Test that resources.load_as_dataset returns a Dataset object with the expected content."""
        path_test_data = iati.core.resources.get_test_data_path('valid')

        result = iati.core.resources.load_as_dataset(path_test_data)

        assert isinstance(result, iati.core.Dataset)
        assert '<?xml version="1.0"?>\n\n<iati-activities version="2.02">' in result.xml_str

    def test_load_as_dataset_invalid(self):
        """Test that resources.load_as_dataset raises an error when the provided path does not lead to a file containing valid XML."""
        path_test_data = iati.core.resources.get_test_data_path('invalid')

        with pytest.raises(ValueError):
            _ = iati.core.resources.load_as_dataset(path_test_data)

    def test_load_as_string(self):
        """Test that `resources.load_as_string()` returns a string (python3) or unicode (python2) object with the expected content."""
        path_test_data = iati.core.resources.get_test_data_path('invalid')

        result = iati.core.resources.load_as_string(path_test_data)

        assert isinstance(result, six.string_types)
        assert result == 'This is a string that is not valid XML\n'

    @pytest.mark.parametrize("load_method", [iati.core.resources.load_as_bytes, iati.core.resources.load_as_dataset, iati.core.resources.load_as_string])
    def test_load_as_x_non_existing_file(self, load_method):
        """Test that `resources.load_as_bytes()` returns a bytes object with the expected content."""
        path_test_data = iati.core.resources.get_test_data_path('this-file-does-not-exist')

        # python 2/3 compatibility - FileNotFoundError introduced at Python 3
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError  # pylint: disable=redefined-builtin,invalid-name

        with pytest.raises(FileNotFoundError):
            _ = load_method(path_test_data)

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
