"""A file to define py.test fixtures that are used across more than one test file."""
import pytest
import iati.core.constants

@pytest.fixture(params=['no_arguments', None] + iati.core.constants.STANDARD_VERSIONS)
def standard_version_optional(request):
    """Return a list that can be used as variable positional parameters (i.e. `*standard_version_optional`) to test.
    This can then be used in tests which have an optional parameter for the version, or expect None.

    Returns:
        list: Either i) an empty list, ii) a list containing None, or iii) a string which corresponds to a version of the Standard.

    """
    arg = request.param

    if arg == 'no_arguments':
        return []
    else:
        return [arg]
