"""A module containing tests for the library implementation of accessing utilities."""
from lxml import etree
import pytest
import iati.core.resources
import iati.core.tests.utilities
import iati.core.utilities


class TestUtilities(object):
    """A container for tests relating to utilities"""

    def test_add_namespace_schema_new(self):
        """Check that an additional namespace can be added to a Schema.

        Todo:
            Deal with required changes to iati.core.constants.NSMAP.

            Add a similar test for Datasets.
        """
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        ns_name = 'xi'
        ns_uri = 'http://www.w3.org/2001/XInclude'

        initial_nsmap = schema._schema_base_tree.getroot().nsmap
        schema = iati.core.utilities.add_namespace(schema, ns_name, ns_uri)
        new_nsmap = schema._schema_base_tree.getroot().nsmap

        assert len(new_nsmap) == len(initial_nsmap) + 1
        assert ns_name not in initial_nsmap
        assert ns_name in new_nsmap
        assert new_nsmap[ns_name] == ns_uri

    def test_add_namespace_schema_already_present(self):
        """Check that attempting to add a namespace that already exists to a Schema does not modify the nsmap.

        Todo:
            Add a similar test for Datasets.
        """
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        ns_name = 'xsd'
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        initial_nsmap = schema._schema_base_tree.getroot().nsmap
        schema = iati.core.utilities.add_namespace(schema, ns_name, ns_uri)
        new_nsmap = schema._schema_base_tree.getroot().nsmap

        assert len(new_nsmap) == len(initial_nsmap)
        assert ns_name in initial_nsmap
        assert ns_name in new_nsmap
        assert initial_nsmap[ns_name] == ns_uri
        assert new_nsmap[ns_name] == ns_uri

    @pytest.mark.parametrize("not_a_schema", iati.core.tests.utilities.find_parameter_by_type([], False))
    def test_add_namespace_no_schema(self, not_a_schema):
        """Check that attempting to add a namespace to something that isn't a Schema raises an error."""
        ns_name = 'xsd'
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        try:
            _ = iati.core.utilities.add_namespace(not_a_schema, ns_name, ns_uri)
        except TypeError:
            assert True
        else:  # pragma: no cover
            assert False

    @pytest.mark.parametrize("ns_name", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_add_namespace_nsname_non_str(self, ns_name):
        """Check that attempting to add a namespace with a name that is not a string acts correctly.

        Todo:
            Determine whether to attempt cast to string or raise an error.
        """
        pass

    @pytest.mark.parametrize("ns_name", [''])
    def test_add_namespace_nsname_invalid_str(self, ns_name):
        """Check that attempting to add a namespace with a name that is an invalid string.

        Todo:
            Add more tests - for syntax, see:
                https://www.w3.org/TR/REC-xml-names/#NT-NSAttName
        """
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        ns_uri = 'http://www.w3.org/2001/XMLSchema'

        try:
            _ = iati.core.utilities.add_namespace(schema, ns_name, ns_uri)
        except ValueError:
            assert True
        else:  # pragma: no cover
            assert False

    @pytest.mark.parametrize("ns_uri", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_add_namespace_nsname_non_str(self, ns_uri):
        """Check that attempting to add a namespace uri that is not a string acts correctly.

        Todo:
            Determine whether to attempt cast to string or raise an error.
        """
        pass

    @pytest.mark.parametrize("ns_uri", [''])
    def test_add_namespace_nsname_invalid_str(self, ns_uri):
        """Check that attempting to add a namespace that is an invalid string.

        Note:
            While a valid URI, an empty string is not a valid namespace - https://www.w3.org/TR/REC-xml-names/#iri-use https://www.ietf.org/rfc/rfc2396.txt

        Todo:

        """
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        ns_name = 'testname'

        try:
            _ = iati.core.utilities.add_namespace(schema, ns_name, ns_uri)
        except ValueError:
            assert True
        else:  # pragma: no cover
            assert False

    def test_convert_tree_to_schema(self):
        """Check that an etree can be converted to a Schema."""
        path = iati.core.resources.path_schema('iati-activities-schema')

        tree = iati.core.resources.load_as_tree(path)
        if not tree:  # pragma: no cover
            assert False
        schema = iati.core.utilities.convert_tree_to_schema(tree)

        assert isinstance(schema, etree.XMLSchema)

    def test_convert_xml_to_tree(self):
        """Check that a valid XML string can be converted to an etree."""
        xml = '<parent><child /></parent>'

        tree = iati.core.utilities.convert_xml_to_tree(xml)

        assert isinstance(tree, etree._Element)  # pylint: disable=protected-access
        assert tree.tag == 'parent'
        assert len(tree.getchildren()) == 1
        assert tree.getchildren()[0].tag == 'child'
        assert len(tree.getchildren()[0].getchildren()) == 0

    def test_convert_xml_to_tree_invalid_str(self):
        """Check that an invalid string raises an error when an attempt is made to convert it to an etree."""
        not_xml = "this is not XML"

        try:
            _ = iati.core.utilities.convert_xml_to_tree(not_xml)
        except etree.XMLSyntaxError:
            assert True
        else:  # pragma: no cover
            assert False

    @pytest.mark.parametrize("not_xml", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_convert_xml_to_tree_not_str(self, not_xml):
        """Check that an invalid string raises an error when an attempt is made to convert it to an etree.
        """
        try:
            _ = iati.core.utilities.convert_xml_to_tree(not_xml)
        except ValueError:
            assert True
        else:  # pragma: no cover
            assert False

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
