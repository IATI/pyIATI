"""A module containing tests for the library implementation of accessing resources."""
import collections
from decimal import Decimal
import os
import re
import pytest
import iati.constants
import iati.resources
import iati.utilities
import iati.validator
import iati.version
import iati.tests.resources


class TestResourceConstants(object):
    """A container for tests relating to checks of resource constants."""

    @pytest.mark.parametrize('folder_path', [
        iati.resources.BASE_PATH_STANDARD,
        iati.resources.BASE_PATH_LIB_DATA
    ])
    def test_base_folders_valid_values(self, folder_path):
        """Test that constants that should be folder paths 2-levels deep are paths that are 2-levels deep, rooted at the base folder.

        The contents of the second component is tested in test_folder_names_valid_values()
        """
        path_components = folder_path.split(os.path.sep)

        assert len(path_components) == 2
        assert path_components[0] == iati.resources.BASE_PATH

    @pytest.mark.parametrize('folder_name', [
        iati.resources.BASE_PATH,
        iati.resources.BASE_PATH_STANDARD.split(os.path.sep).pop(),
        iati.resources.BASE_PATH_LIB_DATA.split(os.path.sep).pop(),
        iati.resources.PATH_CODELISTS,
        iati.resources.PATH_SCHEMAS,
        iati.resources.PATH_RULESETS,
        iati.resources.PATH_VERSION_INDEPENDENT
    ])
    def test_folder_names_valid_values(self, folder_name):
        """Test that constants that should be folder names are lower case strings separated by underscores."""
        folder_name_regex = re.compile(r'^([a-z]+_)*[a-z]+$')

        assert re.match(folder_name_regex, folder_name)

    @pytest.mark.parametrize('file_name', [
        iati.resources.FILE_CODELIST_MAPPING,
        iati.resources.FILE_RULESET_SCHEMA_NAME,
        iati.resources.FILE_RULESET_STANDARD_NAME,
        iati.resources.FILE_SCHEMA_ACTIVITY_NAME,
        iati.resources.FILE_SCHEMA_ORGANISATION_NAME
    ])
    def test_file_names_valid_values(self, file_name):
        """Test that constants that should be file names are lower case strings separated by hyphens or underscores."""
        file_name_regex = re.compile(r'^([a-z]+[\-_])*[a-z]+$')

        assert re.match(file_name_regex, file_name)

    @pytest.mark.parametrize('file_extension', [
        iati.resources.FILE_CODELIST_EXTENSION,
        iati.resources.FILE_DATA_EXTENSION,
        iati.resources.FILE_RULESET_EXTENSION,
        iati.resources.FILE_SCHEMA_EXTENSION
    ])
    def test_file_extensions_valid_values(self, file_extension):
        """Test that constants that should be file extensions are a dot followed by a lower case string."""
        file_extension_regex = re.compile(r'^\.[a-z]+$')

        assert re.match(file_extension_regex, file_extension)


class TestResourceFilesystemPaths(object):
    """A container for tests relating to specific filesystem paths."""

    def test_resource_filesystem_path(self, filename_no_meaning):
        """Check that resource file names are found correctly."""
        base_path = iati.resources.resource_filesystem_path('')
        full_path = iati.resources.resource_filesystem_path(filename_no_meaning)

        assert len(full_path) > len(filename_no_meaning)
        assert full_path.startswith(base_path)
        assert full_path.endswith(filename_no_meaning)
        assert os.path.abspath(full_path) == full_path

    def test_resource_filesystem_path_folders(self, folderpath_no_meaning):
        """Check that resource folder names are found correctly."""
        base_path = iati.resources.resource_filesystem_path('')
        full_path = iati.resources.resource_filesystem_path(folderpath_no_meaning)

        assert len(full_path) > len(folderpath_no_meaning)
        assert full_path.startswith(base_path)
        assert full_path.endswith(folderpath_no_meaning)
        assert os.path.abspath(full_path) + os.path.sep == full_path

    def test_resource_filesystem_path_empty_path(self, filepath_empty):
        """Check that the base resource folder is located when given an empty filepath."""
        full_path = iati.resources.resource_filesystem_path(filepath_empty)

        assert full_path != ''
        assert os.path.isdir(full_path)


class TestResourceLibData(object):
    """A container for tests relating to handling paths for pyIATI library-specific data."""

    def test_create_lib_data_path(self, filename_no_meaning):
        """Check that library data can be located."""
        full_path = iati.resources.create_lib_data_path(filename_no_meaning)

        assert iati.resources.BASE_PATH_LIB_DATA in full_path
        assert full_path.endswith(filename_no_meaning)


class TestResourceHandlingInvalidPaths(object):
    """A container for tests relating to handling paths that are invalid and being passed to functions that are version-independent."""

    @pytest.fixture(params=[
        iati.resources.create_lib_data_path,
        iati.resources.resource_filesystem_path
    ])
    def resource_func(self, request):
        """A resource function that takes in file paths as an input."""
        return request.param

    def test_create_lib_data_path_empty_path(self, filepath_empty):
        """Check that a ValueError is raised when given an empty filepath."""
        with pytest.raises(ValueError):
            iati.resources.create_lib_data_path(filepath_empty)

    def test_create_lib_data_path_valueerr(self, filepath_invalid_value, resource_func):
        """Check that functions cause a value error when given a string that cannot be a filepath."""
        with pytest.raises(ValueError):
            resource_func(filepath_invalid_value)

    def test_create_lib_data_path_typeerr(self, filepath_invalid_type, resource_func):
        """Check that functions cause a type error when given a path of an incorrect type."""
        with pytest.raises(TypeError):
            resource_func(filepath_invalid_type)


class TestResourcePathComponents(object):
    """A container for tests relating to generation of component parts of a resource path."""

    @pytest.mark.parametrize('version, expected_version_foldername', [
        ('2.02', '2-02'),
        ('2.01', '2-01'),
        ('1.05', '1-05'),
        ('1.04', '1-04'),
        ('1.03', '1-03'),
        ('1.02', '1-02'),
        ('1.01', '1-01'),
        ('2.1.10', '2-02'),
        ('2.0.5', '2-01'),
        ('1.4.4', '1-05'),
        ('1.3.3', '1-04'),
        ('1.2.2', '1-03'),
        ('1.1.1', '1-02'),
        ('1.1.0', '1-02'),
        ('1.0.0', '1-01'),
        (Decimal('1.05'), '1-05'),
        (Decimal('1.04'), '1-04'),
        (Decimal('1.03'), '1-03'),
        (Decimal('1.02'), '1-02'),
        (Decimal('1.01'), '1-01'),
        (iati.Version('2.02'), '2-02'),
        (iati.Version('2.01'), '2-01'),
        (iati.Version('1.05'), '1-05'),
        (iati.Version('1.04'), '1-04'),
        (iati.Version('1.03'), '1-03'),
        (iati.Version('1.02'), '1-02'),
        (iati.Version('1.01'), '1-01'),
        ('1', '1'),
        ('2', '2'),
        (iati.version.STANDARD_VERSION_ANY, iati.resources.PATH_VERSION_INDEPENDENT)
    ])
    @pytest.mark.latest_version('2.02')
    def test_folder_name_for_version_generation_known(self, version, expected_version_foldername):
        """Check that the correct folder name is returned for known version numbers."""
        folder_name = iati.resources.folder_name_for_version(version)

        assert expected_version_foldername == folder_name

    def test_folder_name_for_version_generation_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when trying to create a folder name for an unknown version."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(std_ver_all_mixedinst_valid_unknown)

    def test_folder_name_for_version_valueerr(self, std_ver_all_uninst_valueerr):
        """Check that a version of the Standard of the correct type, but an incorrect value raises a ValueError."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_valueerr)

    def test_folder_name_for_version_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that a version of the Standard of the correct type, but an incorrect value raises a TypeError."""
        with pytest.raises(TypeError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_typeerr)

    def test_folder_name_for_version_requires_version(self):
        """Check that a version must be specified when requesting a folder name for a version (there is no default)."""
        with pytest.raises(TypeError):
            iati.resources.folder_name_for_version()  # pylint: disable=no-value-for-parameter


class TestResoucePathCreationEntireStandard(object):
    """A container for tests relating to generating entire filepaths for any part of the Standard."""

    def test_folder_path_for_version_known(self, std_ver_any_mixedinst_valid_known):
        """Check that expected components are present within folder paths for data for known versions of the IATI Standard."""
        expected_components = ['resources', 'standard', iati.resources.BASE_PATH_STANDARD]

        version_folder = iati.resources.folder_name_for_version(std_ver_any_mixedinst_valid_known)
        full_path = iati.resources.folder_path_for_version(std_ver_any_mixedinst_valid_known)

        assert version_folder in full_path
        for component in expected_components:
            assert component in full_path

    def test_folder_path_for_version_unknown_valueerr(self, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when trying to create a path for an unknown version of the IATI Standard."""
        with pytest.raises(ValueError):
            iati.resources.folder_path_for_version(std_ver_all_mixedinst_valid_unknown)

    def test_folder_path_for_version_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that a TypeError is raised when trying to create a folder path for a value of a type that cannot be a version number."""
        with pytest.raises(TypeError):
            iati.resources.folder_path_for_version(std_ver_all_uninst_typeerr)

    def test_folder_path_for_version_requires_version(self):
        """Check that a version must be specified when requesting a folder path for a version (there is no default)."""
        with pytest.raises(TypeError):
            iati.resources.folder_path_for_version()  # pylint: disable=no-value-for-parameter

    def test_path_for_version_known(self, filename_no_meaning, std_ver_any_mixedinst_valid_known):
        """Check that expected components are present within absolute paths for data for known versions of the IATI Standard."""
        relative_path = iati.resources.folder_path_for_version(std_ver_any_mixedinst_valid_known)
        abs_path = iati.resources.path_for_version(filename_no_meaning, std_ver_any_mixedinst_valid_known)

        assert abs_path.startswith(os.path.sep)
        assert relative_path in abs_path
        assert abs_path.endswith(filename_no_meaning)

    def test_path_for_version_empty_path(self, filepath_empty, std_ver_any_mixedinst_valid_known):
        """Check that expected components are present within an absolute path for an empty path within a version folder."""
        relative_path = iati.resources.folder_path_for_version(std_ver_any_mixedinst_valid_known)
        abs_path = iati.resources.path_for_version(filepath_empty, std_ver_any_mixedinst_valid_known)

        assert abs_path.startswith(os.path.sep)
        assert relative_path in abs_path
        assert abs_path.split(os.path.sep).pop() == filepath_empty
        # there are not currently folders for integer resource versions
        if isinstance(std_ver_any_mixedinst_valid_known, iati.Version) or std_ver_any_mixedinst_valid_known == iati.version.STANDARD_VERSION_ANY:
            assert os.path.isdir(abs_path)

    def test_path_for_version_unknown_ver_valueerr(self, filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when trying to create a path for an unknown version of the IATI Standard."""
        with pytest.raises(ValueError):
            iati.resources.path_for_version(filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown)

    def test_path_for_version_unknown_ver_typeerr(self, filename_no_meaning_single, std_ver_all_uninst_typeerr):
        """Check that a TypeError is raised when trying to create a folder path for a value of a type that cannot be a version number."""
        with pytest.raises(TypeError):
            iati.resources.path_for_version(filename_no_meaning_single, std_ver_all_uninst_typeerr)

    def test_path_for_version_requires_version(self, filename_no_meaning_single):
        """Check that a version must be specified when requesting a path for a version (there is no default)."""
        with pytest.raises(TypeError):
            iati.resources.path_for_version(filename_no_meaning_single)  # pylint: disable=no-value-for-parameter

    def test_path_for_version_path_valueerr(self, filepath_invalid_value, std_ver_minor_inst_valid_single):
        """Check that a ValueError is raised when trying to create a path from a string that cannot be a filepath."""
        with pytest.raises(ValueError):
            iati.resources.path_for_version(filepath_invalid_value, std_ver_minor_inst_valid_single)

    def test_path_for_version_path_typeerr(self, filepath_invalid_type, std_ver_minor_inst_valid_single):
        """Check that a TypeError is raised when trying to create an absolute path from a path of an incorrect type."""
        with pytest.raises(TypeError):
            iati.resources.path_for_version(filepath_invalid_type, std_ver_minor_inst_valid_single)


class TestResourcePathCreationCodelistMapping(object):
    """A container for tests relating to creating Codelist Mapping File paths."""

    def test_create_codelist_mapping_path_minor(self, std_ver_minor_mixedinst_valid_known):
        """Check that there is a single Codelist Mapping File for minor versions."""
        version_folder = iati.resources.folder_name_for_version(std_ver_minor_mixedinst_valid_known)
        path = iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_known)

        assert isinstance(path, str)
        assert path.endswith(iati.resources.FILE_CODELIST_MAPPING + iati.resources.FILE_CODELIST_EXTENSION)
        assert version_folder in path

    def test_create_codelist_mapping_path_major(self, std_ver_major_uninst_valid_known):
        """Check that requesting a Codelist Mapping File for a major version returns the same path as for the last minor within the major."""
        minor_version = max(iati.version.versions_for_integer(std_ver_major_uninst_valid_known))

        path_major = iati.resources.create_codelist_mapping_path(std_ver_major_uninst_valid_known)
        path_minor = iati.resources.create_codelist_mapping_path(minor_version)

        assert path_major == path_minor

    def test_create_codelist_mapping_path_version_independent(self):
        """Check that a ValueError is raised when requesting a version-independent Codelist Mapping File."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(iati.version.STANDARD_VERSION_ANY)

    def test_create_codelist_mapping_path_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when requesting a Codelist Mapping file for an unknown version of the Standard."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(std_ver_all_mixedinst_valid_unknown)


class TestResourcePathCreationCoreComponents(object):
    """A container for tests relating to path creation for core components in the IATI Standard.

    Core components include Codelists, Rulesets and Schemas.
    Each of these should act equivalently across different version and path inputs since their parameters are the same.
    Schemas are available at more versions than Rulesets, though this is not an issue since the create_x_path() functions do not check whether a path actually exists.
    """

    @pytest.fixture(params=[
        iati.resources.create_codelist_path,
        iati.resources.create_ruleset_path,
        iati.resources.create_schema_path
    ])
    def func_to_test(self, request):
        """Return a function to test."""
        return request.param

    @pytest.fixture(params=[
        iati.resources.create_ruleset_path,
        iati.resources.create_schema_path
    ])
    def func_to_test_decimalised_integers(self, request):
        """Return a function to test that treats integers as the latest minor within the major."""
        return request.param

    @pytest.fixture(params=[
        (iati.resources.create_codelist_path, iati.resources.FILE_CODELIST_EXTENSION, iati.resources.PATH_CODELISTS),
        (iati.resources.create_ruleset_path, iati.resources.FILE_RULESET_EXTENSION, iati.resources.PATH_RULESETS),
        (iati.resources.create_schema_path, iati.resources.FILE_SCHEMA_EXTENSION, iati.resources.PATH_SCHEMAS)
    ])
    def func_plus_expected_data(self, request):
        """Return a tuple containing a function to test, plus the extension and a component that should be present in the returned path."""
        output = collections.namedtuple('output', 'func_to_test expected_extension expected_component')
        return output(func_to_test=request.param[0], expected_extension=request.param[1], expected_component=request.param[2])

    def test_create_path_minor_known(self, filename_no_meaning, std_ver_minor_independent_mixedinst_valid_known, func_plus_expected_data):
        """Check that the expected components are present in a path from a generation function at a known minor or independent version of the Standard."""
        version_folder = iati.resources.folder_name_for_version(std_ver_minor_independent_mixedinst_valid_known)
        full_path = func_plus_expected_data.func_to_test(filename_no_meaning, std_ver_minor_independent_mixedinst_valid_known)

        assert isinstance(full_path, str)
        assert full_path.endswith(filename_no_meaning + func_plus_expected_data.expected_extension)
        assert version_folder in full_path
        assert func_plus_expected_data.expected_component in full_path

    def test_create_path_major_known(self, filename_no_meaning_single, std_ver_major_uninst_valid_known):
        """Check that a generation function returns a value for a major version.

        This is relevant to Codelists, but not other components. These are tested separately.
        """
        version_folder = iati.resources.folder_name_for_version(std_ver_major_uninst_valid_known)
        full_path = iati.resources.create_codelist_path(filename_no_meaning_single, std_ver_major_uninst_valid_known)

        assert isinstance(full_path, str)
        assert full_path.endswith(filename_no_meaning_single + iati.resources.FILE_CODELIST_EXTENSION)
        assert os.path.sep + version_folder + os.path.sep in full_path
        assert iati.resources.PATH_CODELISTS in full_path

    def test_create_path_major_known_decimalised_integers(self, filename_no_meaning_single, std_ver_major_uninst_valid_known, func_to_test_decimalised_integers):
        """Check that a generation function returns the same value for a major version as the last minor within the major.

        This is relevant to some Standard components, though not all. As such, it uses a different fixture to other functions in this class.
        """
        minor_version = max(iati.version.versions_for_integer(std_ver_major_uninst_valid_known))

        major_path = func_to_test_decimalised_integers(filename_no_meaning_single, std_ver_major_uninst_valid_known)
        minor_path = func_to_test_decimalised_integers(filename_no_meaning_single, minor_version)

        assert major_path == minor_path

    def test_create_path_no_version(self, filename_no_meaning_single, func_to_test):
        """Check that specifying a version of the Standard to create a path for is required."""
        with pytest.raises(TypeError):
            func_to_test(filename_no_meaning_single)

    def test_create_path_unknown(self, filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown, func_to_test):
        """Check that a ValueError is raised when using a generation function to create a path for a at an unknown version of the Standard."""
        with pytest.raises(ValueError):
            func_to_test(filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown)

    def test_create_path_ver_typerr(self, filename_no_meaning_single, std_ver_all_uninst_typeerr, func_to_test):
        """Check that a TypeError is raised when using a generation function to create a path from a version of an incorrect type."""
        with pytest.raises(TypeError):
            func_to_test(filename_no_meaning_single, std_ver_all_uninst_typeerr)

    def test_create_path_path_valueerr(self, filepath_invalid_value, std_ver_minor_inst_valid_single, func_to_test):
        """Check that a ValueError is raised when providing a generation function a path to work from that is a string that cannot be a filepath."""
        with pytest.raises(ValueError):
            func_to_test(filepath_invalid_value, std_ver_minor_inst_valid_single)

    def test_create_path_path_typeerr(self, filepath_invalid_type, std_ver_minor_inst_valid_single, func_to_test):
        """Check that a TypeError is raised when providing a generation function a path to work from that is of a type that cannot be a filepath."""
        with pytest.raises(TypeError):
            func_to_test(filepath_invalid_type, std_ver_minor_inst_valid_single)


class TestResourceGetCodelistPaths(object):
    """A container for get_codelist_paths() tests."""

    def test_find_codelist_paths(self, codelist_lengths_by_version):
        """Check that all codelist paths are being found.

        This covers major, minor and version-independent.
        """
        paths = iati.resources.get_codelist_paths(codelist_lengths_by_version.version)

        assert len(paths) == codelist_lengths_by_version.expected_length
        for path in paths:
            assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
            assert iati.resources.PATH_CODELISTS in path

    def test_get_codelist_mapping_paths_independent(self):
        """Test getting a list of version-independent Codelist files.

        Todo:
            Look to better determine how to access the different categories of Codelist.

        """
        result = iati.resources.get_codelist_paths(iati.version.STANDARD_VERSION_ANY)

        assert result == []

    def test_get_codelist_paths_minor_partsupport(self, std_ver_minor_mixedinst_valid_partsupport):
        """Test getting a list of Codelist paths. The requested version is partially supported by pyIATI."""
        result = iati.resources.get_codelist_paths(std_ver_minor_mixedinst_valid_partsupport)

        assert result == []

    def test_get_codelist_paths_minor_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Test getting a list of Codelist paths. The requested version is not known by pyIATI."""
        result = iati.resources.get_codelist_paths(std_ver_all_mixedinst_valid_unknown)

        assert result == []


class TestResourceGetCodelistMappingPaths(object):
    """A container for get_codelist_mapping_paths() tests.

    Note:
        This class contains very similar tests to the equivalent for Rulesets. They are different because the Ruleset creation function takes two arguments, not one.
    """

    def test_get_codelist_mapping_paths_minor_fullsupport(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Test getting a list of Codelist Mapping paths. The requested version is fully supported by pyIATI."""
        result = iati.resources.get_codelist_mapping_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(result) == 1
        assert result[0] == iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_fullsupport)

    def test_get_codelist_mapping_paths_independent(self):
        """Test getting a list of version-independent Codelist Mapping files."""
        result = iati.resources.get_codelist_mapping_paths(iati.version.STANDARD_VERSION_ANY)

        assert result == []

    def test_get_codelist_mapping_paths_minor_partsupport(self, std_ver_minor_mixedinst_valid_partsupport):
        """Test getting a list of Codelist Mapping paths. The requested version is partially supported by pyIATI."""
        result = iati.resources.get_codelist_mapping_paths(std_ver_minor_mixedinst_valid_partsupport)

        assert result == []

    def test_get_codelist_mapping_paths_minor_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Test getting a list of Codelist Mapping paths. The requested version is not known by pyIATI."""
        result = iati.resources.get_codelist_mapping_paths(std_ver_all_mixedinst_valid_unknown)

        assert result == []

    def test_get_codelist_mapping_paths_major_known(self, std_ver_major_uninst_valid_known):
        """Test getting a list of Codelist Mapping paths. The requested version is a known integer version. The list should contain paths for each supported minor within the major."""
        supported_versions_at_major = [version for version in iati.version.versions_for_integer(std_ver_major_uninst_valid_known) if version in iati.version.STANDARD_VERSIONS_SUPPORTED]
        expected_path_count = len(supported_versions_at_major)

        result = iati.resources.get_codelist_mapping_paths(std_ver_major_uninst_valid_known)

        assert len(result) == expected_path_count
        for version in supported_versions_at_major:
            assert iati.resources.create_codelist_mapping_path(version) in result


class TestResourceGetRulesetPaths(object):
    """A container for get_ruleset_paths() tests."""

    def test_get_ruleset_paths_minor_fullsupport(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Test getting a list of Ruleset paths. The requested version is fully supported by pyIATI."""
        result = iati.resources.get_ruleset_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(result) == 1
        assert result[0] == iati.resources.create_ruleset_path(iati.resources.FILE_RULESET_STANDARD_NAME, std_ver_minor_mixedinst_valid_fullsupport)

    def test_get_ruleset_paths_independent(self):
        """Test getting a list of version-independent standard Rulesets."""
        result = iati.resources.get_ruleset_paths(iati.version.STANDARD_VERSION_ANY)

        assert result == []

    def test_get_ruleset_paths_minor_partsupport(self, std_ver_minor_mixedinst_valid_partsupport):
        """Test getting a list of Ruleset paths. The requested version is partially supported by pyIATI."""
        result = iati.resources.get_ruleset_paths(std_ver_minor_mixedinst_valid_partsupport)

        assert result == []

    def test_get_ruleset_paths_minor_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Test getting a list of Ruleset paths. The requested version is not known by pyIATI."""
        result = iati.resources.get_ruleset_paths(std_ver_all_mixedinst_valid_unknown)

        assert result == []

    def test_get_ruleset_paths_major_known(self, std_ver_major_uninst_valid_known):
        """Test getting a list of Ruleset paths. The requested version is a known integer version. The list should contain paths for each supported minor within the major."""
        supported_versions_at_major = [version for version in iati.version.versions_for_integer(std_ver_major_uninst_valid_known) if version in iati.version.STANDARD_VERSIONS_SUPPORTED]
        expected_path_count = len(supported_versions_at_major)

        result = iati.resources.get_ruleset_paths(std_ver_major_uninst_valid_known)

        assert len(result) == expected_path_count
        for version in supported_versions_at_major:
            assert iati.resources.create_ruleset_path(iati.resources.FILE_RULESET_STANDARD_NAME, version) in result


class TestResourceGetSchemaPaths(object):
    """A container for get_x_schema_paths() tests."""

    @pytest.fixture(params=[
        (iati.resources.get_activity_schema_paths, iati.resources.FILE_SCHEMA_ACTIVITY_NAME),
        (iati.resources.get_organisation_schema_paths, iati.resources.FILE_SCHEMA_ORGANISATION_NAME)
    ])
    def func_and_name(self, request):
        """Return a named tuple containing a function to generate the paths for a type of Schema, plus the name of the Schema."""
        output = collections.namedtuple('output', 'func schema_name')
        return output(func=request.param[0], schema_name=request.param[1])

    @pytest.fixture(params=[
        iati.resources.get_all_schema_paths,
        iati.resources.get_activity_schema_paths,
        iati.resources.get_organisation_schema_paths
    ])
    def schema_path_func_all(self, request):
        """Return a function that returns a list of paths for Schema resources."""
        return request.param

    def test_get_schema_paths_minor_known(self, std_ver_minor_mixedinst_valid_known, func_and_name):
        """Test getting a list of Org or Activity Schema paths. The requested version is known by pyIATI."""
        result = func_and_name.func(std_ver_minor_mixedinst_valid_known)

        assert len(result) == 1
        assert result[0] == iati.resources.create_schema_path(func_and_name.schema_name, std_ver_minor_mixedinst_valid_known)

    def test_get_schema_paths_minor_unknown(self, std_ver_all_mixedinst_valid_unknown, schema_path_func_all):
        """Test getting a list of Org or Activity Schema paths. The requested version is not known by pyIATI."""
        result = schema_path_func_all(std_ver_all_mixedinst_valid_unknown)

        assert result == []

    def test_get_schema_paths_independent(self, schema_path_func_all):
        """Test getting a list of version-independent Org or Activity Schemas."""
        result = schema_path_func_all(iati.version.STANDARD_VERSION_ANY)

        assert result == []

    def test_get_schema_paths_major_known(self, std_ver_major_uninst_valid_known, func_and_name):
        """Test getting a list of Org or Activity Schema paths. The requested version is a known integer version. The list should contain paths for each supported minor within the major."""
        versions_at_major = [version for version in iati.version.versions_for_integer(std_ver_major_uninst_valid_known)]
        expected_path_count = len(versions_at_major)

        result = func_and_name.func(std_ver_major_uninst_valid_known)

        assert len(result) == expected_path_count
        for version in versions_at_major:
            assert iati.resources.create_schema_path(func_and_name.schema_name, version) in result

    def test_get_all_schema_paths_minor_known(self, std_ver_minor_mixedinst_valid_known):
        """Test getting a list of all Schema paths. The requested version is known by pyIATI."""
        activity_path = iati.resources.get_activity_schema_paths(std_ver_minor_mixedinst_valid_known)[0]
        org_path = iati.resources.get_organisation_schema_paths(std_ver_minor_mixedinst_valid_known)[0]

        result = iati.resources.get_all_schema_paths(std_ver_minor_mixedinst_valid_known)

        assert len(result) == 2
        assert activity_path in result
        assert org_path in result

        # ensure the paths have at least a minimum amount of content in the files they reference
        for path in result:
            assert os.path.getsize(path) > 10000

    def test_get_all_schema_paths_major_known(self, std_ver_major_uninst_valid_known):
        """Test getting a list of all Schema paths. The requested version is a known integer version. The list should contain paths for each supported minor within the major."""
        versions_at_major = [version for version in iati.version.versions_for_integer(std_ver_major_uninst_valid_known)]
        expected_path_count = len(versions_at_major) * 2

        activity_paths = iati.resources.get_activity_schema_paths(std_ver_major_uninst_valid_known)
        org_paths = iati.resources.get_organisation_schema_paths(std_ver_major_uninst_valid_known)

        result = iati.resources.get_all_schema_paths(std_ver_major_uninst_valid_known)

        assert len(result) == expected_path_count
        for path in activity_paths:
            assert path in result
        for path in org_paths:
            assert path in result


class TestResourceGetPathsNotAVersion(object):
    """A container for get_x_path() tests where the function is provided a value that cannot represent a version."""

    @pytest.fixture(params=[
        iati.resources.get_codelist_paths,
        iati.resources.get_codelist_mapping_paths,
        iati.resources.get_ruleset_paths,
        iati.resources.get_all_schema_paths,
        iati.resources.get_activity_schema_paths,
        iati.resources.get_organisation_schema_paths
    ])
    def func_to_test(self, request):
        """Return a function to test the behavior of. The function takes a single argument, which takes a value that can represent a version number."""
        return request.param

    def test_get_x_path_valueerr(self, std_ver_all_uninst_valueerr, func_to_test):
        """Check that a ValueError is raised when requesting paths for an value that cannot be a version of the Standard."""
        with pytest.raises(ValueError):
            func_to_test(std_ver_all_uninst_valueerr)

    def test_get_x_path_no_version(self, func_to_test):
        """Check that a TypeError is raised when requesting paths without specifying a version."""
        with pytest.raises(TypeError):
            func_to_test()

    def test_get_x_path_typerr(self, std_ver_all_uninst_typeerr, func_to_test):
        """Check that a TypeError is raised when requesting paths for a version of an incorrect type."""
        with pytest.raises(TypeError):
            func_to_test(std_ver_all_uninst_typeerr)


class TestResourceTestDataFolders(object):
    """A container for tests relating to resource folders."""

    @pytest.mark.parametrize('version, expected_num_paths', [
        ('2.02', 237),
        ('2.01', 217),
        ('1.05', 17),
        ('1.04', 17),
        ('1.03', 17),
        ('1.02', 17),
        ('1.01', 16),
        ('1', 0),
        ('2', 0),
        (iati.version.STANDARD_VERSION_ANY, 0)
    ])
    @pytest.mark.latest_version('2.02')
    def test_get_test_data_paths_in_folder(self, version, expected_num_paths):
        """Check that test data is being found in specified subfolders.

        Look for the number of paths in the `ssot-activity-xml-fail` folder.
        """
        paths = iati.tests.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail', version)

        assert len(paths) == expected_num_paths
