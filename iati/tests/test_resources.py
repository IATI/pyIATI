"""A module containing tests for the library implementation of accessing resources."""
from decimal import Decimal
from lxml import etree
import pytest
import iati.constants
import iati.resources
import iati.utilities
import iati.validator
import iati.version
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
        (iati.version.STANDARD_VERSION_ANY, 'version-independent')
    ])
    def test_folder_name_for_version(self, version, expected_version_foldername):
        """Check that expected components are present within folder paths."""
        path = iati.resources.folder_name_for_version(version)

        assert expected_version_foldername == path

    def test_folder_name_for_version_valueerr(self, std_ver_all_uninst_valueerr):
        """Check that an version of the Standard of the correct type, but an incorrect value raises a ValueError."""
        with pytest.raises(ValueError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_valueerr)

    def test_folder_name_for_version_typeerr(self, std_ver_all_uninst_typeerr):
        """Check that an version of the Standard of the correct type, but an incorrect value raises a TypeError."""
        with pytest.raises(TypeError):
            iati.resources.folder_name_for_version(std_ver_all_uninst_typeerr)

    @pytest.mark.parametrize('path_component', [
        'resources',
        'standard'
    ])
    def test_folder_path_for_version(self, std_ver_minor_mixedinst_valid_fullsupport, path_component):
        """Check that expected components are present within folder paths."""
        path = iati.resources.folder_path_for_version(std_ver_minor_mixedinst_valid_fullsupport)
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

    def test_create_codelist_mapping_path_invalid_value(self, std_ver_all_uninst_valueerr):
        """Check that a ValueError is raised when requesting with a version of the correct type, but that cannot represent a version."""
        with pytest.raises(ValueError):
            iati.resources.create_codelist_mapping_path(std_ver_all_uninst_valueerr)

    def test_create_codelist_mapping_path_invalid_value(self, std_ver_all_uninst_typeerr):
        """Check that a ValueError is raised when requesting with a version of the wrong type."""
        with pytest.raises(TypeError):
            iati.resources.create_codelist_mapping_path(std_ver_all_uninst_typeerr)

    def test_create_codelist_mapping_path_is_xml(self, std_ver_minor_mixedinst_valid_fullsupport):
        """Check that the Codelist Mapping File path points to a valid XML file."""
        path = iati.resources.create_codelist_mapping_path(std_ver_minor_mixedinst_valid_fullsupport)

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
