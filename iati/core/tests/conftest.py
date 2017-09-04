"""A file to define py.test fixtures that are used across more than one test file."""
import pytest
import iati.core.constants


@pytest.fixture(params=[
    ('2.02', 62),  # There are 38 embedded codelists at v2.02, plus 24 non-embedded codelists (which are valid for any version)
    ('2.01', 61),  # There are 37 embedded codelists at v2.01, plus 24 non-embedded codelists (which are valid for any version)
    ('1.05', 59),  # There are 35 embedded codelists at v1.05, plus 24 non-embedded codelists (which are valid for any version)
    ('1.04', 59)  # There are 35 embedded codelists at v1.04, plus 24 non-embedded codelists (which are valid for any version)
])
def codelist_lengths_by_version(request):
    return request.param


@pytest.fixture(params=['no_arguments', None] + iati.core.constants.STANDARD_VERSIONS)
def standard_version_optional(request):
    """Return a list that can be passed to a function using the argument list unpacking functionality - see https://docs.python.org/3.6/tutorial/controlflow.html#unpacking-argument-lists
    For example, the returned list can be used to test functions (such as `get_all_codelist_paths`) which has an optional parameter for the version, or can expect version=None.,
    In this case test usage would be `get_all_codelist_paths(*standard_version_optional)`.

    Returns:
        list: Either i) an empty list, ii) a list containing None, or iii) a string which corresponds to a version of the Standard.

    """
    if request.param == 'no_arguments':
        return []
    else:
        return [request.param]
