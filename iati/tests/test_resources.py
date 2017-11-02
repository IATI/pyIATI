"""A module containing tests for the library implementation of accessing resources."""
from lxml import etree
import pytest
import six
import iati.constants
import iati.resources
import iati.validator


class TestResources(object):
    """A container for tests relating to resources in general."""

    def test_resource_filename(self):
        """Check that resource file names are found correctly.

        Todo:
            Implement better assertions.

        """
        path = iati.resources.PATH_SCHEMAS
        filename = iati.resources.resource_filename(path)

        assert len(filename) > len(path)
        assert filename.endswith(path)


class TestResourceFolders(object):
    """A container for tests relating to resource folders."""

    @pytest.mark.parametrize('version, expected_version_foldername', [
        ('2.02', '202'),
        ('2.01', '201'),
        ('1.05', '105'),
        ('1.04', '104')
    ])
    def test_get_folder_name_for_version(self, version, expected_version_foldername):
        """Check that expected components are present within folder paths."""
        path = iati.resources.get_folder_name_for_version(version)
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
            iati.resources.get_folder_name_for_version(version)

    @pytest.mark.parametrize('path_component', [
        'resources',
        'standard'
    ])
    def test_get_folder_path_for_version(self, standard_version_optional, path_component):
        """Check that expected components are present within folder paths."""
        path = iati.resources.get_folder_path_for_version(*standard_version_optional)
        assert path_component in path

    def test_get_test_data_paths_in_folder(self):
        """Check that test data is being found in specified subfolders.

        Todo:
            Deal with multiple versions.

        """
        paths = iati.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail')

        assert len(paths) == 237


class TestResourceLibraryData(object):
    """A container for tests relating to pyIATI resources."""

    @pytest.mark.parametrize('file_name', [
        'name',
        'Name.xml',
    ])
    def test_get_lib_data_path(self, file_name):
        """Check that library data can be located."""
        path = iati.resources.get_lib_data_path(file_name)

        assert iati.resources.BASE_PATH_LIB_DATA != ''
        assert iati.resources.BASE_PATH_LIB_DATA in path
        assert file_name == path[-len(file_name):]


class TestResourceCodelists(object):
    """A container for tests relating to Codelist resources."""

    def test_codelist_flow_type(self, standard_version_optional):
        """Check that the FlowType codelist is loaded as a string and contains content."""
        path = iati.resources.get_codelist_path('FlowType', *standard_version_optional)

        content = iati.resources.load_as_string(path)

        assert len(content) > 3200
        assert iati.validator.is_xml(content)

    def test_find_codelist_paths(self, codelist_lengths_by_version):
        """Check that all codelist paths are being found."""
        paths = iati.resources.get_all_codelist_paths(codelist_lengths_by_version[0])

        assert len(paths) == codelist_lengths_by_version[1]
        for path in paths:
            assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
            assert iati.resources.PATH_CODELISTS in path

    @pytest.mark.parametrize('codelist', [
        'Name',
        'Name.xml',
    ])
    def test_get_codelist_path_name(self, standard_version_optional, codelist):
        """Check that a codelist path is found from just a name."""
        path = iati.resources.get_codelist_path(codelist, *standard_version_optional)

        assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
        assert path.count(iati.resources.FILE_CODELIST_EXTENSION) == 1
        assert iati.resources.PATH_CODELISTS in path

    def test_get_codelist_mapping_path(self, standard_version_optional):
        """Check that the Codelist Mapping File path points to a valid XML file."""
        path = iati.resources.get_codelist_mapping_path(*standard_version_optional)

        content = iati.resources.load_as_string(path)

        assert len(content) > 5000
        assert iati.validator.is_xml(content)


class TestResourceSchemas(object):
    """A container for tests relating to Schema resources."""

    def test_get_all_activity_schema_paths(self, standard_version_optional):
        """Check that all activity schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        activity_paths = iati.resources.get_all_activity_schema_paths(*standard_version_optional)

        assert len(activity_paths) == 1

    def test_get_all_organisation_schema_paths(self, standard_version_optional):
        """Check that all organisation schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        organisation_paths = iati.resources.get_all_organisation_schema_paths(*standard_version_optional)

        assert len(organisation_paths) == 1

    def test_find_schema_paths(self, standard_version_optional):
        """Check that both the activity and organisation schema paths are being found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        paths = iati.resources.get_all_schema_paths(*standard_version_optional)

        assert len(paths) == 2

    @pytest.mark.parametrize('get_schema_path_function', [
        iati.resources.get_all_schema_paths,
        iati.resources.get_all_activity_schema_paths,
        iati.resources.get_all_organisation_schema_paths
    ])
    def test_find_schema_paths_file_extension(self, standard_version_optional, get_schema_path_function):
        """Check that the correct file extension is present within file paths returned by get_all_*schema_paths functions."""
        paths = get_schema_path_function(*standard_version_optional)

        for path in paths:
            assert path[-4:] == iati.resources.FILE_SCHEMA_EXTENSION

    def test_schema_activity_string(self):
        """Check that the Activity schema file contains content."""
        path = iati.resources.get_schema_path('iati-activities-schema')

        content = iati.resources.load_as_string(path)

        assert len(content) > 130000

    def test_schema_activity_tree(self):
        """Check that the Activity schema loads into an XML Tree.

        This additionally involves checking that imported schemas also work.

        """
        path = iati.resources.get_schema_path('iati-activities-schema')
        schema = iati.resources.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)  # pylint: disable=protected-access


class TestResourceLoading(object):
    """A container for tests relating to loading resources."""

    def test_load_as_bytes(self):
        """Test that resources.load_as_bytes returns a bytes object with the expected content."""
        path_test_data = iati.resources.get_test_data_path('invalid')

        result = iati.resources.load_as_bytes(path_test_data)

        assert isinstance(result, bytes)
        assert result == 'This is a string that is not valid XML\n'.encode()

    def test_load_as_dataset(self):
        """Test that resources.load_as_dataset returns a Dataset object with the expected content."""
        path_test_data = iati.resources.get_test_data_path('valid')

        result = iati.resources.load_as_dataset(path_test_data)

        assert isinstance(result, iati.Dataset)
        assert '<?xml version="1.0"?>\n\n<iati-activities version="2.02">' in result.xml_str

    def test_load_as_dataset_invalid(self):
        """Test that resources.load_as_dataset raises an error when the provided path does not lead to a file containing valid XML."""
        path_test_data = iati.resources.get_test_data_path('invalid')

        with pytest.raises(ValueError):
            _ = iati.resources.load_as_dataset(path_test_data)

    def test_load_as_string(self):
        """Test that `resources.load_as_string()` returns a string (python3) or unicode (python2) object with the expected content."""
        path_test_data = iati.resources.get_test_data_path('invalid')

        result = iati.resources.load_as_string(path_test_data)

        assert isinstance(result, six.string_types)
        assert result == 'This is a string that is not valid XML\n'

    @pytest.mark.parametrize("load_method", [iati.resources.load_as_bytes, iati.resources.load_as_dataset, iati.resources.load_as_string])
    def test_load_as_x_non_existing_file(self, load_method):
        """Test that `resources.load_as_bytes()` returns a bytes object with the expected content."""
        path_test_data = iati.resources.get_test_data_path('this-file-does-not-exist')

        # python 2/3 compatibility - FileNotFoundError introduced at Python 3
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError  # pylint: disable=redefined-builtin,invalid-name

        with pytest.raises(FileNotFoundError):
            _ = load_method(path_test_data)

    @pytest.mark.parametrize("file_to_load", [
        'dataset-encoding/valid-windows-1252.xml'
    ])
    def test_load_as_string_restricted_charset(self, file_to_load):
        """Test that Datasets can be loaded from files encoded with a limited charset."""
        path = iati.resources.get_test_data_path(file_to_load)

        data_str = iati.resources.load_as_string(path)
        dataset = iati.Dataset(data_str)
        str_of_interest = dataset.xml_tree.xpath('//reporting-org/narrative/text()')[0]

        # the character of interest is in windows-1252, but is different from ASCII
        # python2/3 compatibility: encode string as UTF-8
        assert str_of_interest.encode('utf-8') == b'\xc5\xb8'

    @pytest.mark.parametrize("file_to_load", [
        'dataset-encoding/valid-UTF-8.xml',
        'dataset-encoding/valid-UTF-16LE.xml',
        'dataset-encoding/valid-UTF-16BE.xml',
        'dataset-encoding/valid-UTF-16.xml',
        'dataset-encoding/valid-UTF-32.xml'
    ])
    def test_load_as_string_unicode(self, file_to_load):
        """Test that Datasets can be loaded from files encoded with various unicode encodings."""
        path = iati.resources.get_test_data_path(file_to_load)

        data_str = iati.resources.load_as_string(path)
        dataset = iati.Dataset(data_str)
        str_of_interest = dataset.xml_tree.xpath('//reporting-org/narrative/text()')[0]

        # the tested characters are all in the code range 004000-00FFFF
        # this means that they are 3-bit at UTF-8, 2 bit as UTF-16 and 4-bit as UTF-32 in 8-bit environments
        # https://en.wikipedia.org/wiki/Comparison_of_Unicode_encodings#Eight-bit_environments
        # python2/3 compatibility: encode string as UTF-8
        assert str_of_interest.encode('utf-8') == b'\xe4\xb6\x8c\xe4\xb9\xa8\xe4\xbc\xb6\xe4\xbe\x97\xe5\x80\x97\xe5\x82\x88\xe5\x84\x88\xe5\x89\x89\xe5\x94\x99\xe8\xac\x9c\xe8\xb0\x8b\xee\x82\xb1\xee\x82\xb2\xee\x82\xb3\xee\x82\xb5\xee\x82\xb8\xee\x82\xba\xee\x82\xbb\xee\x82\xbc\xee\x82\xbd\xee\x82\xbe\xee\x83\x8e\xee\x83\x8f\xee\x84\xa8\xee\x84\xa9\xe4\xb6\x8c\xe4\xb9\xa8\xe4\xbc\xb6\xe4\xbe\x97\xe5\x80\x97\xe5\x82\x88\xe5\x84\x88\xe5\x89\x89\xe5\x94\x99\xe8\xac\x9c\xe8\xb0\x8b\xee\x82\xb1\xee\x82\xb2\xee\x82\xb3\xee\x82\xb5\xee\x82\xb8\xee\x82\xba\xee\x82\xbb\xee\x82\xbc\xee\x82\xbd\xee\x82\xbe\xee\x83\x8e\xee\x83\x8f\xee\x84\xa8\xee\x84\xa9\xe4\xb6\x8c\xe4\xb9\xa8\xe4\xbc\xb6\xe4\xbe\x97\xe5\x80\x97\xe5\x82\x88\xe5\x84\x88\xe5\x89\x89\xe5\x94\x99\xe8\xac\x9c\xe8\xb0\x8b\xee\x82\xb1\xee\x82\xb2\xee\x82\xb3\xee\x82\xb5\xee\x82\xb8\xee\x82\xba\xee\x82\xbb\xee\x82\xbc\xee\x82\xbd\xee\x82\xbe\xee\x83\x8e\xee\x83\x8f\xee\x84\xa8\xee\x84\xa9'  # noqa: ignore=E501  # pylint: disable=line-too-long

    @pytest.mark.parametrize("file_to_load", [
        'dataset-encoding/valid-undetectable-encoding.xml'
    ])
    def test_load_as_string_undetectable_encoding(self, file_to_load):
        """Test that when an encoding cannot be detected, the correct error is raised.

        The file with an undetectable encoding is a UTF-16LE file without a BOM.

        """
        path = iati.resources.get_test_data_path(file_to_load)

        with pytest.raises(ValueError):
            _ = iati.resources.load_as_string(path)
