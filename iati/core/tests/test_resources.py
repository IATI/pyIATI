import pytest

import iati.core.resources

class TestResources(object):
    """A container for tests relating to resources"""

    def test_flow_type_codelist(self):
        """Check that the FlowType codelist contains content"""
        path = iati.core.resources.path_codelist('FlowType')

        content = iati.core.resources.load_as_string(path)

        assert 100 < len(content)
