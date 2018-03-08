"""Pytest fixtures for utility purposes."""
import pytest


@pytest.fixture
def latest_version_202(request):
    """Mark that the test supports the latest version of the Standard. This is said to be 2.02.

    Note:
        To demonstrate that a function supports a newer version of the Standard than 2.02, an equivalent fixture for a newer version must be used.

    """
    latest_version_marker = pytest.mark.latest_version('2.02')
    request.applymarker(latest_version_marker)
