"""A module containing tests for the library implementation of accessing resources."""
from decimal import Decimal
import os
import re
from lxml import etree
import pytest
import iati.constants
import iati.resources
import iati.utilities
import iati.validator
import iati.version
import iati.tests.resources


@pytest.mark.new_tests
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
        folder_name_regex = re.compile('^([a-z]+_)*[a-z]+$')

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
        file_name_regex = re.compile('^([a-z]+[\-_])*[a-z]+$')

        assert re.match(file_name_regex, file_name)

    @pytest.mark.parametrize('file_extension', [
        iati.resources.FILE_CODELIST_EXTENSION,
        iati.resources.FILE_DATA_EXTENSION,
        iati.resources.FILE_RULESET_EXTENSION,
        iati.resources.FILE_SCHEMA_EXTENSION
    ])
    def test_file_extensions_valid_values(self, file_extension):
        """Test that constants that should be file extensions are a dot followed by a lower case string."""
        file_extension_regex = re.compile('^\.[a-z]+$')

        assert re.match(file_extension_regex, file_extension)


@pytest.mark.new_tests
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

        assert len(full_path)
        assert os.path.isdir(full_path)


@pytest.mark.new_tests
class TestResourceLibData(object):
    """A container for tests relating to handling paths for pyIATI library-specific data."""

    def test_create_lib_data_path(self, filename_no_meaning):
        """Check that library data can be located."""
        full_path = iati.resources.create_lib_data_path(filename_no_meaning)

        assert iati.resources.BASE_PATH_LIB_DATA in full_path
        assert full_path.endswith(filename_no_meaning)


@pytest.mark.new_tests
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


@pytest.mark.new_tests
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
    def test_version_folder_name_generation_known(self, version, expected_version_foldername):
        """Check that the correct folder name is returned for known version numbers."""
        folder_name = iati.resources.folder_name_for_version(version)

        assert expected_version_foldername == folder_name

    def test_version_folder_name_generation_unknown(self, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when trying to create a folder name for an unknown version."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(std_ver_all_mixedinst_valid_unknown)

    def test_folder_name_for_version_valueerr(self, std_ver_all_uninst_valueerr):
        """Check that an version of the Standard of the correct type, but an incorrect value raises a ValueError."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_valueerr)

    def test_folder_name_for_version_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that an version of the Standard of the correct type, but an incorrect value raises a TypeError."""
        with pytest.raises(TypeError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_typeerr)


@pytest.mark.new_tests
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

    def test_path_for_version_path_valueerr(self, filepath_invalid_value, std_ver_minor_inst_valid_single):
        """Check that a ValueError is raised when trying to create a path from a string that cannot be a filepath."""
        with pytest.raises(ValueError):
            iati.resources.path_for_version(filepath_invalid_value, std_ver_minor_inst_valid_single)

    def test_path_for_version_path_typeerr(self, filepath_invalid_type, std_ver_minor_inst_valid_single):
        """Check that a TypeError is raised when trying to create an absolute path from a path of an incorrect type."""
        with pytest.raises(TypeError):
            iati.resources.path_for_version(filepath_invalid_type, std_ver_minor_inst_valid_single)


@pytest.mark.new_tests
class TestResourcePathCreationRulesets(object):
    """A container for tests relating to Ruleset path creation."""

    def test_create_ruleset_path_minor_known(self, filename_no_meaning, std_ver_minor_independent_mixedinst_valid_known):
        """Check that the expected components are present in a path for a Ruleset at a known minor or independent version of the Standard."""
        version_folder = iati.resources.folder_name_for_version(std_ver_minor_independent_mixedinst_valid_known)
        full_path = iati.resources.create_ruleset_path(filename_no_meaning, std_ver_minor_independent_mixedinst_valid_known)

        assert full_path.endswith(filename_no_meaning + iati.resources.FILE_RULESET_EXTENSION)
        assert version_folder in full_path
        assert iati.resources.PATH_RULESETS in full_path

    def test_create_ruleset_path_major_known(self, filename_no_meaning_single, std_ver_major_uninst_valid_known):
        """Check that asking for a Ruleset path for a major version returns the same value as the last minor within the major."""
        minor_version = max(iati.version.versions_for_integer(std_ver_major_uninst_valid_known))

        major_path = iati.resources.create_ruleset_path(filename_no_meaning_single, std_ver_major_uninst_valid_known)
        minor_path = iati.resources.create_ruleset_path(filename_no_meaning_single, minor_version)

        assert major_path == minor_path

    def test_create_ruleset_path_no_version(self, filename_no_meaning_single):
        """Check that specifying a version of the Standard to create a path for is required."""
        with pytest.raises(TypeError):
            iati.resources.create_ruleset_path(filename_no_meaning_single)

    def test_create_ruleset_path_unknown(self, filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown):
        """Check that a ValueError is raised when trying to create a path for a Ruleset at an unknown version of the Standard."""
        with pytest.raises(ValueError):
            iati.resources.create_ruleset_path(filename_no_meaning_single, std_ver_all_mixedinst_valid_unknown)

    def test_create_ruleset_path_ver_typerr(self, filename_no_meaning_single, std_ver_all_uninst_typeerr):
        """Check that a TypeError is raised when trying to create a path for a Ruleset from a version of an incorrect type."""
        with pytest.raises(TypeError):
            iati.resources.create_ruleset_path(filename_no_meaning_single, std_ver_all_uninst_typeerr)

    def test_create_ruleset_path_path_valueerr(self, filepath_invalid_value, std_ver_minor_inst_valid_single):
        """Check that a ValueError is raised when trying to ruleset path for a path that is a string that cannot be a filepath."""
        with pytest.raises(ValueError):
            iati.resources.create_ruleset_path(filepath_invalid_value, std_ver_minor_inst_valid_single)

    def test_create_ruleset_path_path_typeerr(self, filepath_invalid_type, std_ver_minor_inst_valid_single):
        """Check that a TypeError is raised when trying to ruleset path for a path that is of a type that cannot be a filepath."""
        with pytest.raises(TypeError):
            iati.resources.create_ruleset_path(filepath_invalid_type, std_ver_minor_inst_valid_single)


class TestResourceFolders(object):
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
    def test_get_test_data_paths_in_folder(self, version, expected_num_paths):
        """Check that test data is being found in specified subfolders.

        Look for the number of paths in the `ssot-activity-xml-fail` folder.
        """
        paths = iati.tests.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail', version)

        assert len(paths) == expected_num_paths


class TestResourceCreatePath(object):
    """A container for tests relating to creating paths."""

    @pytest.fixture(params=[
        'AidType', 'FlowType', 'Language',  # Codelist names that are valid at all versions
        'BudgetStatus', 'OtherIdentifierType', 'PolicyMarkerVocabulary',  # Codelist names that are valid at some versions, but not all
        'invalid-codelist-name'  # Codelist name that is not a valid Codelist
    ])
    def potential_codelist_name(self, request):
        """Return a potential Codelist name."""
        return request.param

    def test_create_codelist_path(self, potential_codelist_name, std_ver_any_mixedinst_valid_known):
        """Check that a Codelist path is correctly created."""
        path = iati.resources.create_codelist_path(potential_codelist_name, std_ver_any_mixedinst_valid_known)

        assert isinstance(path, str)
        assert iati.resources.folder_name_for_version(std_ver_any_mixedinst_valid_known) in path

    @pytest.mark.parametrize("not_a_str", iati.tests.utilities.generate_test_types(['str'], True))
    def test_create_codelist_path_non_str_name(self, not_a_str, std_ver_any_mixedinst_valid_known):
        """Check that a TypeError is raised when requesting a Codelist with a non-string name."""
        with pytest.raises(TypeError):
            iati.resources.create_codelist_path(not_a_str, std_ver_any_mixedinst_valid_known)

    def test_create_codelist_path_version_valueerr(self, std_ver_all_uninst_valueerr):
        """Check that a ValueError is raised when requesting a Codelist with a version of the correct type, but that cannot represent a version."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_path('maybe-codelist-name', std_ver_all_uninst_valueerr)

    def test_create_codelist_path_version_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that a TypeError is raised when requesting a Codelist with a version of the wrong type."""
        with pytest.raises(TypeError):
            iati.resources.create_codelist_path('maybe-codelist-name', std_ver_all_uninst_typeerr)

    def test_create_codelist_mapping_path_minor(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that there is a single Codelist Mapping File for minor versions."""
        path = iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_fullsupport)

        assert isinstance(path, str)
        assert iati.resources.folder_name_for_version(std_ver_minor_mixedinst_valid_fullsupport) in path

    def test_create_codelist_mapping_path_major(self, std_ver_major_uninst_valid_known):
        """Check that requesting a Codelist Mapping File for a major version returns the same path as for the last minor within the major."""
        standard_version_minor = max(iati.version.versions_for_integer(std_ver_major_uninst_valid_known))

        path_major = iati.resources.create_codelist_mapping_path(std_ver_major_uninst_valid_known)
        path_minor = iati.resources.create_codelist_mapping_path(standard_version_minor)

        assert path_major == path_minor

    def test_create_codelist_mapping_path_version_independent(self):
        """Check that a ValueError is raised when requesting a version-independent Codelist Mapping File."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(iati.version.STANDARD_VERSION_ANY)

    def test_create_codelist_mapping_path_valueerr(self, std_ver_all_uninst_valueerr):
        """Check that a ValueError is raised when requesting with a version of the correct type, but that cannot represent a version."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(std_ver_all_uninst_valueerr)

    def test_create_codelist_mapping_path_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that a ValueError is raised when requesting with a version of the wrong type."""
        with pytest.raises(TypeError):
            iati.resources.create_codelist_mapping_path(std_ver_all_uninst_typeerr)

    def test_create_codelist_mapping_path_is_xml(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that the Codelist Mapping File path points to a valid XML file."""
        path = iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_fullsupport)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 5000
        assert iati.validator.is_xml(content)


class TestResourceCodelists(object):
    """A container for tests relating to Codelist resources."""

    def test_codelist_flow_type(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that the FlowType codelist is loaded as a string and contains content."""
        path = iati.resources.create_codelist_path('FlowType', std_ver_minor_mixedinst_valid_fullsupport)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 3200
        assert iati.validator.is_xml(content)

    def test_find_codelist_paths(self, codelist_lengths_by_version):
        """Check that all codelist paths are being found."""
        paths = iati.resources.get_codelist_paths(codelist_lengths_by_version[0])

        assert len(paths) == codelist_lengths_by_version[1]
        for path in paths:
            assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
            assert iati.resources.PATH_CODELISTS in path

    @pytest.mark.parametrize('codelist', [
        'Name',
        'Name.xml',
    ])
    def test_get_codelist_path_name(self, std_ver_minor_mixedinst_valid_fullsupport, codelist):
        """Check that a codelist path is found from just a name."""
        path = iati.resources.create_codelist_path(codelist, std_ver_minor_mixedinst_valid_fullsupport)

        assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
        assert path.count(iati.resources.FILE_CODELIST_EXTENSION) == 1
        assert iati.resources.PATH_CODELISTS in path

    def test_get_codelist_mapping_paths(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that all codelist mapping paths are found."""
        codelist_mapping_paths = iati.resources.get_codelist_mapping_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(codelist_mapping_paths) == 1

    def test_create_codelist_mapping_path(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that the Codelist Mapping File path points to a valid XML file."""
        path = iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_fullsupport)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 5000
        assert iati.validator.is_xml(content)


class TestResourceRulesets(object):
    """A container for tests relating to Ruleset resources."""

    def test_get_ruleset_paths(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that all ruleset paths are found."""
        ruleset_paths = iati.resources.get_ruleset_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(ruleset_paths) == 1


class TestResourceSchemas(object):
    """A container for tests relating to Schema resources."""

    def test_get_activity_schema_paths(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that all activity schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        activity_paths = iati.resources.get_activity_schema_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(activity_paths) == 1

    def test_get_organisation_schema_paths(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that all organisation schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        organisation_paths = iati.resources.get_organisation_schema_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(organisation_paths) == 1

    def test_find_schema_paths(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that both the activity and organisation schema paths are being found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        paths = iati.resources.get_all_schema_paths(std_ver_minor_mixedinst_valid_fullsupport)

        assert len(paths) == 2

    @pytest.mark.parametrize('create_schema_path_function', [
        iati.resources.get_all_schema_paths,
        iati.resources.get_activity_schema_paths,
        iati.resources.get_organisation_schema_paths
    ])
    def test_find_schema_paths_file_extension(self, std_ver_minor_mixedinst_valid_fullsupport, create_schema_path_function):
        """Check that the correct file extension is present within file paths returned by get_all_*schema_paths functions."""
        paths = create_schema_path_function(std_ver_minor_mixedinst_valid_fullsupport)

        for path in paths:
            assert path[-4:] == iati.resources.FILE_SCHEMA_EXTENSION

    def test_schema_activity_string(self, std_ver_minor_inst_valid_known):
        """Check that the Activity schema file contains content.

        Todo:
            Change fixture to mixedinst.

        """
        path = iati.resources.create_schema_path('iati-activities-schema', std_ver_minor_inst_valid_known)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 50000

    def test_schema_activity_tree(self, std_ver_minor_inst_valid_known):
        """Check that the Activity schema loads into an XML Tree.

        This additionally involves checking that imported schemas also work.

        Todo:
            Change fixture to mixedinst.

        """
        path = iati.resources.create_schema_path('iati-activities-schema', std_ver_minor_inst_valid_known)
        schema = iati.utilities.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)  # pylint: disable=protected-access
