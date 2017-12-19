"""A module containing tests for the library implementation of accessing resources."""
from lxml import etree
import pytest
import iati.constants
import iati.resources
import iati.validator
import iati.utilities
import iati.tests.resources


class TestResources(object):
    """A container for tests relating to resources in general."""

    def test_resource_filesystem_path(self):
        """Check that resource file names are found correctly.

        Todo:
            Implement better assertions.

        """
        path = iati.resources.PATH_SCHEMAS
        filename = iati.resources.resource_filesystem_path(path)

        assert len(filename) > len(path)
        assert filename.endswith(path)


class TestResourceFolders(object):
    """A container for tests relating to resource folders."""

    @pytest.mark.parametrize('version, expected_version_foldername', [
        ('2.02', '2-02'),
        ('2.01', '2-01'),
        ('1.05', '1-05'),
        ('1.04', '1-04'),
        ('1.03', '1-03'),
        ('1.02', '1-02'),
        ('1.01', '1-01'),
        ('1', '1'),
        ('2', '2'),
        (None, 'version-independent')
    ])
    def test_folder_name_for_version(self, version, expected_version_foldername):
        """Check that expected components are present within folder paths."""
        path = iati.resources.folder_name_for_version(version)

        assert expected_version_foldername == path

    @pytest.mark.parametrize('version', [
        '1.00',
        1,
        1.01,  # A version must be specified as a string
        'string'
    ])
    def test_folder_name_for_version_invalid_version(self, version):
        """Check that an invalid version of the Standard raises a ValueError exception."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(version)

    @pytest.mark.parametrize('path_component', [
        'resources',
        'standard'
    ])
    def test_folder_path_for_version(self, standard_version_optional, path_component):
        """Check that expected components are present within folder paths."""
        path = iati.resources.folder_path_for_version(*standard_version_optional)
        assert path_component in path

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
        (None, 0)
    ])
    def test_get_test_data_paths_in_folder(self, version, expected_num_paths):
        """Check that test data is being found in specified subfolders.

        Look for the number of paths in the `ssot-activity-xml-fail` folder.
        """
        paths = iati.tests.resources.get_test_data_paths_in_folder('ssot-activity-xml-fail', version)

        assert len(paths) == expected_num_paths


class TestResourceCreatePath(object):
    """A container for tests relating to creating paths."""

    @pytest.mark.parametrize('cl_name', [
        'AidType', 'FlowType', 'Language',  # Codelist names that are valid at all versions
        'BudgetStatus', 'OtherIdentifierType', 'PolicyMarkerVocabulary',  # Codelist names that are valid at some versions, but not all
        'invalid-codelist-name'  # Codelist name that is not a valid Codelist
    ])
    def test_create_codelist_path(self, cl_name, standard_version_all_types):
        """Check that a Codelist path is correctly created."""
        path = iati.resources.create_codelist_path(cl_name, *standard_version_all_types)

        assert isinstance(path, str)
        assert iati.resources.folder_name_for_version(*standard_version_all_types) in path

    @pytest.mark.parametrize("not_a_str", iati.tests.utilities.generate_test_types(['none', 'str'], True))
    def test_create_codelist_path_non_str_name(self, not_a_str, standard_version_all_types):
        """Check that a Error is raised when requesting a Codelist with a non-string name."""
        with pytest.raises(TypeError):
            iati.resources.create_codelist_path(not_a_str, *standard_version_all_types)

    @pytest.mark.parametrize("not_a_version", iati.tests.utilities.generate_test_types(['none'], True))
    def test_create_codelist_path_fuzzed_version(self, not_a_version):
        """Check that a ValueError is raised when requesting a Codelist with a fuzzed version."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_path('a-name-for-a-codelist', not_a_version)

    def test_create_codelist_mapping_path_minor(self, standard_version_minor):
        """Check that there is a single Codelist Mapping File for minor versions."""
        path = iati.resources.create_codelist_mapping_path(standard_version_minor)

        assert isinstance(path, str)
        assert iati.resources.folder_name_for_version(standard_version_minor) in path

    def test_create_codelist_mapping_path_major(self, standard_version_major):
        """Check that requesting a Codelist Mapping File for a major version returns the same path as for the last minor within the major."""
        standard_version_minor = max(iati.utilities.versions_for_integer(standard_version_major))

        path_major = iati.resources.create_codelist_mapping_path(standard_version_major)
        path_minor = iati.resources.create_codelist_mapping_path(standard_version_minor)

        assert path_major == path_minor

    def test_create_codelist_mapping_path_version_independent(self):
        """Check that a ValueError is raised when requesting a version-independent Codelist Mapping File."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path()

    @pytest.mark.parametrize("not_a_version", iati.tests.utilities.generate_test_types(['none'], True))
    def test_create_codelist_mapping_path_invalid_value(self, not_a_version):
        """Check that a ValueError is raised when requesting a fuzzed Codelist Mapping File."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(not_a_version)

    def test_create_codelist_mapping_path_is_xml(self, standard_version_optional):
        """Check that the Codelist Mapping File path points to a valid XML file."""
        path = iati.resources.create_codelist_mapping_path(*standard_version_optional)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 5000
        assert iati.validator.is_xml(content)


class TestResourceLibraryData(object):
    """A container for tests relating to pyIATI resources."""

    @pytest.mark.parametrize('file_name', [
        'name',
        'Name.xml',
    ])
    def test_create_lib_data_path(self, file_name):
        """Check that library data can be located."""
        path = iati.resources.create_lib_data_path(file_name)

        assert iati.resources.BASE_PATH_LIB_DATA != ''
        assert iati.resources.BASE_PATH_LIB_DATA in path
        assert file_name == path[-len(file_name):]


class TestResourceCodelists(object):
    """A container for tests relating to Codelist resources."""

    def test_codelist_flow_type(self, standard_version_optional):
        """Check that the FlowType codelist is loaded as a string and contains content."""
        path = iati.resources.create_codelist_path('FlowType', *standard_version_optional)

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
    def test_get_codelist_path_name(self, standard_version_optional, codelist):
        """Check that a codelist path is found from just a name."""
        path = iati.resources.create_codelist_path(codelist, *standard_version_optional)

        assert path[-4:] == iati.resources.FILE_CODELIST_EXTENSION
        assert path.count(iati.resources.FILE_CODELIST_EXTENSION) == 1
        assert iati.resources.PATH_CODELISTS in path

    def test_get_codelist_mapping_paths(self, standard_version_optional):
        """Check that all codelist mapping paths are found."""
        codelist_mapping_paths = iati.resources.get_codelist_mapping_paths(*standard_version_optional)

        assert len(codelist_mapping_paths) == 1


class TestResourceRulesets(object):
    """A container for tests relating to Ruleset resources."""

    def test_get_ruleset_paths(self, standard_version_optional):
        """Check that all ruleset paths are found."""
        ruleset_paths = iati.resources.get_ruleset_paths(*standard_version_optional)

        assert len(ruleset_paths) == 1


class TestResourceSchemas(object):
    """A container for tests relating to Schema resources."""

    def test_get_activity_schema_paths(self, standard_version_optional):
        """Check that all activity schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        activity_paths = iati.resources.get_activity_schema_paths(*standard_version_optional)

        assert len(activity_paths) == 1

    def test_get_organisation_schema_paths(self, standard_version_optional):
        """Check that all organisation schema paths are found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        organisation_paths = iati.resources.get_organisation_schema_paths(*standard_version_optional)

        assert len(organisation_paths) == 1

    def test_find_schema_paths(self, standard_version_optional):
        """Check that both the activity and organisation schema paths are being found.

        Todo:
            Handle all paths to schemas being found correctly.

        """
        paths = iati.resources.get_all_schema_paths(*standard_version_optional)

        assert len(paths) == 2

    @pytest.mark.parametrize('create_schema_path_function', [
        iati.resources.get_all_schema_paths,
        iati.resources.get_activity_schema_paths,
        iati.resources.get_organisation_schema_paths
    ])
    def test_find_schema_paths_file_extension(self, standard_version_optional, create_schema_path_function):
        """Check that the correct file extension is present within file paths returned by get_all_*schema_paths functions."""
        paths = create_schema_path_function(*standard_version_optional)

        for path in paths:
            assert path[-4:] == iati.resources.FILE_SCHEMA_EXTENSION

    def test_schema_activity_string(self, standard_version_all):
        """Check that the Activity schema file contains content."""
        path = iati.resources.create_schema_path('iati-activities-schema', standard_version_all)

        content = iati.utilities.load_as_string(path)

        assert len(content) > 50000

    def test_schema_activity_tree(self, standard_version_all):
        """Check that the Activity schema loads into an XML Tree.

        This additionally involves checking that imported schemas also work.

        """
        path = iati.resources.create_schema_path('iati-activities-schema', standard_version_all)
        schema = iati.utilities.load_as_tree(path)

        assert isinstance(schema, etree._ElementTree)  # pylint: disable=protected-access
