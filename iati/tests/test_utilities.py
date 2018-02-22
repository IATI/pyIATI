"""A module containing tests for the library implementation of accessing utilities."""
from lxml import etree
import pytest
import six
import iati.resources
import iati.tests.utilities
import iati.utilities


class TestUtilities(object):
    """A container for tests relating to utilities."""

    @pytest.fixture
    def schema_base_tree(self):
        """Return schema_base_tree.

        Todo:
            Stop this being fixed to 2.02.

        """
        activity_schema_path = iati.resources.get_activity_schema_paths('2.02')[0]

        return iati.ActivitySchema(activity_schema_path)._schema_base_tree  # pylint: disable=protected-access

    def test_add_namespace_schema_new(self, schema_base_tree):
        """Check that an additional namespace can be added to a Schema.

        Todo:
            Deal with required changes to iati.constants.NSMAP.

            Add a similar test for Datasets.

        """
        initial_nsmap = schema_base_tree.getroot().nsmap
        ns_name = 'xi'
        ns_uri = 'http://www.w3.org/2001/XInclude'

        tree = iati.utilities.add_namespace(schema_base_tree, ns_name, ns_uri)
        new_nsmap = tree.getroot().nsmap

        assert len(new_nsmap) == len(initial_nsmap) + 1
        assert ns_name not in initial_nsmap
        assert ns_name in new_nsmap
        assert new_nsmap[ns_name] == ns_uri

    def test_add_namespace_schema_already_present(self, schema_base_tree):
        """Check that attempting to add a namespace that already exists changes nothing if the new URI is the same.

        Todo:
            Add a similar test for Datasets.

        """
        initial_nsmap = schema_base_tree.getroot().nsmap
        ns_name = 'xsd'
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        tree = iati.utilities.add_namespace(schema_base_tree, ns_name, ns_uri)
        new_nsmap = tree.getroot().nsmap

        assert len(new_nsmap) == len(initial_nsmap)
        assert ns_name in initial_nsmap
        assert ns_name in new_nsmap
        assert initial_nsmap[ns_name] == ns_uri
        assert new_nsmap[ns_name] == ns_uri

    def test_add_namespace_schema_already_present_diff_value(self, schema_base_tree):
        """Check that attempting to add a namespace that already exists to a Schema raises an error rather than leading to modification.

        Todo:
            Add a similar test for Datasets.

        """
        ns_name = 'xsd'
        ns_uri = 'http://www.w3.org/2001/XMLSchema-different'

        with pytest.raises(ValueError) as excinfo:
            iati.utilities.add_namespace(schema_base_tree, ns_name, ns_uri)

        assert 'There is already a namespace called' in str(excinfo.value)

    @pytest.mark.parametrize("not_a_tree", iati.tests.utilities.generate_test_types([], True))
    def test_add_namespace_no_schema(self, not_a_tree):
        """Check that attempting to add a namespace to something that isn't a Schema raises an error."""
        ns_name = 'xsd'
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        with pytest.raises(TypeError) as excinfo:
            iati.utilities.add_namespace(not_a_tree, ns_name, ns_uri)

        assert 'The `tree` parameter must be of type `etree._ElementTree` - it was of type' in str(excinfo.value)

    @pytest.mark.parametrize("ns_name", iati.tests.utilities.generate_test_types(['str'], True))
    def test_add_namespace_nsname_non_str(self, ns_name):
        """Check that attempting to add a namespace with a name that is not a string acts correctly.

        Todo:
            Determine whether to attempt cast to string or raise an error.

        """
        pass

    @pytest.mark.parametrize("ns_name", [''])
    def test_add_namespace_nsname_invalid_str(self, ns_name, schema_base_tree):
        """Check that attempting to add a namespace with a name that is an invalid string raises an appropriate error.

        Todo:
            Add more tests - for syntax, see:
                https://www.w3.org/TR/REC-xml-names/#NT-NSAttName

        """
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        with pytest.raises(ValueError) as excinfo:
            iati.utilities.add_namespace(schema_base_tree, ns_name, ns_uri)

        assert 'The `new_ns_name` parameter must be a non-empty string.' in str(excinfo.value)

    @pytest.mark.parametrize("ns_uri", iati.tests.utilities.generate_test_types(['str'], True))
    def test_add_namespace_nsuri_non_str(self, ns_uri):
        """Check that attempting to add a namespace uri that is not a string acts correctly.

        Todo:
            Determine whether to attempt cast to string or raise an error.
        """
        pass

    @pytest.mark.parametrize("ns_uri", [''])
    def test_add_namespace_nsuri_invalid_str(self, ns_uri, schema_base_tree):
        """Check that attempting to add a namespace that is an invalid string raises an appropriate error.

        Note:
            While a valid URI, an empty string is not a valid namespace - https://www.w3.org/TR/REC-xml-names/#iri-use https://www.ietf.org/rfc/rfc2396.txt

        Todo:

        """
        ns_name = 'testname'

        with pytest.raises(ValueError) as excinfo:
            iati.utilities.add_namespace(schema_base_tree, ns_name, ns_uri)

        assert 'The `new_ns_uri` parameter must be a valid URI.' in str(excinfo.value)

    def test_convert_tree_to_schema(self):
        """Check that an etree can be converted to a schema.

        Todo:
            Stop this being fixed to 2.02.

        """
        path = iati.resources.get_activity_schema_paths('2.02')[0]

        tree = iati.utilities.load_as_tree(path)
        if not tree:  # pragma: no cover
            assert False
        schema = iati.utilities.convert_tree_to_schema(tree)

        assert isinstance(schema, etree.XMLSchema)

    def test_convert_xml_to_tree(self):
        """Check that a valid XML string can be converted to an etree."""
        xml = '<parent><child /></parent>'

        tree = iati.utilities.convert_xml_to_tree(xml)

        assert isinstance(tree, etree._Element)  # pylint: disable=protected-access
        assert tree.tag == 'parent'
        assert len(tree.getchildren()) == 1
        assert tree.getchildren()[0].tag == 'child'
        assert not tree.getchildren()[0].getchildren()

    def test_convert_xml_to_tree_invalid_str(self):
        """Check that an invalid string raises an error when an attempt is made to convert it to an etree."""
        not_xml = "this is not XML"

        with pytest.raises(etree.XMLSyntaxError) as excinfo:
            iati.utilities.convert_xml_to_tree(not_xml)

        assert excinfo.typename == 'XMLSyntaxError'

    @pytest.mark.parametrize("not_xml", iati.tests.utilities.generate_test_types(['str'], True))
    def test_convert_xml_to_tree_not_str(self, not_xml):
        """Check that an invalid string raises an error when an attempt is made to convert it to an etree."""
        with pytest.raises(ValueError) as excinfo:
            iati.utilities.convert_xml_to_tree(not_xml)

        assert 'To parse XML into a tree, the XML must be a string, not a' in str(excinfo.value)

    def test_log(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_error(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_exception(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_warning(self):
        """TODO: Implement testing for logging."""
        pass


class TestDefaultVersions(object):
    """A container for tests relating to default versions."""

    def test_versions_for_integer(self, std_ver_major_uninst_valid_known):
        """Check that the each of the decimal versions returned by versions_for_integer starts with the input major version."""
        result = iati.utilities.versions_for_integer(std_ver_major_uninst_valid_known)

        for version in result:
            assert version.major == std_ver_major_uninst_valid_known


class TestFileLoading(object):
    """A container for tests relating to loading files."""

    @pytest.fixture(scope='session')
    def invalid_xml_file_path_non_resource(self, tmpdir_factory):
        """Return a path to an invalid XML file that is not a resource."""
        path_original_data = iati.tests.resources.get_test_data_path('invalid')
        original_data = iati.utilities.load_as_string(path_original_data)

        new_file = tmpdir_factory.mktemp('test_file_loading').join('invalid.xml')
        new_file.write(original_data)

        return new_file.strpath

    @pytest.fixture(params=[
        iati.tests.resources.get_test_data_path('invalid'),
        'non-resource'
    ])  # pylint: disable=invalid-name
    def invalid_xml_file_path(self, request, invalid_xml_file_path_non_resource):
        """Return a path to an invalid XML file."""
        if request.param == 'non-resource':
            return invalid_xml_file_path_non_resource

        return request.param

    @pytest.fixture(scope='session')
    def valid_xml_file_path_non_resource(self, tmpdir_factory):
        """Return a path to a valid XML file that is not a resource."""
        path_original_data = iati.tests.resources.get_test_data_path('valid')
        original_data = iati.utilities.load_as_string(path_original_data)

        new_file = tmpdir_factory.mktemp('test_file_loading').join('valid.xml')
        new_file.write(original_data)

        return new_file.strpath

    @pytest.fixture(params=[
        iati.tests.resources.get_test_data_path('valid'),
        'non-resource'
    ])  # pylint: disable=invalid-name
    def valid_xml_file_path(self, request, valid_xml_file_path_non_resource):
        """Return a path to a valid XML file."""
        if request.param == 'non-resource':
            return valid_xml_file_path_non_resource

        return request.param

    def test_load_as_bytes(self, invalid_xml_file_path):
        """Test that `utilities.load_as_bytes()` returns a bytes object with the expected content."""
        result = iati.utilities.load_as_bytes(invalid_xml_file_path)

        assert isinstance(result, bytes)
        assert result == 'This is a string that is not valid XML\n'.encode()

    def test_load_as_dataset(self, valid_xml_file_path):
        """Test that utilities.load_as_dataset returns a Dataset object with the expected content."""
        result = iati.utilities.load_as_dataset(valid_xml_file_path)

        assert isinstance(result, iati.Dataset)
        assert '<?xml version="1.0"?>\n\n<iati-activities version="2.02">' in result.xml_str

    def test_load_as_dataset_invalid(self, invalid_xml_file_path):
        """Test that `utilities.load_as_dataset()` raises an error when the provided path does not lead to a file containing valid XML."""
        with pytest.raises(ValueError):
            _ = iati.utilities.load_as_dataset(invalid_xml_file_path)

    def test_load_as_string(self, invalid_xml_file_path):
        """Test that `utilities.load_as_string()` returns a string (python3) or unicode (python2) object with the expected content."""
        result = iati.utilities.load_as_string(invalid_xml_file_path)

        assert isinstance(result, six.string_types)
        assert result == 'This is a string that is not valid XML\n'

    @pytest.mark.parametrize("load_method", [
        iati.utilities.load_as_bytes,
        iati.utilities.load_as_dataset,
        iati.utilities.load_as_string
    ])
    def test_load_as_x_non_existing_file(self, load_method):
        """Test that `utilities.load_as_bytes()` returns a bytes object with the expected content."""
        path_test_data = iati.tests.resources.get_test_data_path('this-file-does-not-exist')

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
        path = iati.tests.resources.get_test_data_path(file_to_load)

        data_str = iati.utilities.load_as_string(path)
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
        path = iati.tests.resources.get_test_data_path(file_to_load)

        data_str = iati.utilities.load_as_string(path)
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
        path = iati.tests.resources.get_test_data_path(file_to_load)

        with pytest.raises(ValueError):
            _ = iati.utilities.load_as_string(path)
