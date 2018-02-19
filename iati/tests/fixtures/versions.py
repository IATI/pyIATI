"""Pytest fixtures for specifying versions."""
import pytest
import iati.constants


@pytest.fixture(params=[
    '1.00', '1.0', '2.0', '2.00',  # integer with a zero decimal
    '1.050',  # valid version with extra 0
    '1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2',  # valid versions with the 0 after the decimal point missing
    '3.0', '3.00', '3.1'  # the first few potential values for the next integer
] + iati.tests.utilities.generate_test_types(['none'], True))  # fuzzing data
def std_version_invalid(request):
    """Return a string that isn't a version number, instead being an invalid value."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_MAJOR)
def standard_version_major(request):
    """Return a major version of the IATI Standard."""
    return str(request.param)


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS)
def standard_version_all(request):
    """Return a version of the IATI Standard."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_SUPPORTED)
def standard_version_mandatory(request):
    """Return a list that can be passed to a function using the argument list unpacking functionality.

    For more information about unpacking argument lists, see https://docs.python.org/3.6/tutorial/controlflow.html#unpacking-argument-lists

    Example:
        The returned list can be used to test functions (such as `iati.default.codelists`) which has an optional parameter for the version, or can expect `version=None`. It has an optional parameter after the version.
        In this case test usage would be `iati.default.codelists(*standard_version_mandatory)`.

    Returns:
        list: A string which corresponds to a version of the Standard.

    """
    return [request.param]


@pytest.fixture(params=[version for version in iati.constants.STANDARD_VERSIONS if version not in iati.constants.STANDARD_VERSIONS_SUPPORTED])
def standard_version_partial_support(request):
    """Return a version of the IATI Standard that is partially supported by pyIATI."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_SUPPORTED)
def standard_version_optional(request):
    """Return a list that can be passed to a function using the argument list unpacking functionality.

    For mor information about unpacking argument lists, see https://docs.python.org/3.6/tutorial/controlflow.html#unpacking-argument-lists

    Example:
        The returned list can be used to test functions (such as `get_codelist_paths`) which has an optional parameter for the version, or can expect `version=None`.,
        In this case test usage would be `get_codelist_paths(*standard_version_optional)`.

    Returns:
        list: Either i) an empty list, ii) a list containing None, or iii) a string which corresponds to a version of the Standard.

    """
    return [request.param]
