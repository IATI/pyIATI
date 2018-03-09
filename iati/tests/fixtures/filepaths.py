"""Pytest fixtures for obtaining filepaths."""
import os
import pytest
import iati.tests.utilities


@pytest.fixture(params=[
    'filename-no-extension',
    'filename-with-extension.ext',
    'FilenameMixedCase'
])
def filename_no_meaning(request):
    """Return a filename with no particular meaning."""
    return request.param

@pytest.fixture(params=iati.tests.utilities.generate_test_types(['str'], True))
def filepath_invalid_type(request):
    """Return a value that is of a type that cannot represent a filepath."""
    return request.param

@pytest.fixture
def filepath_empty(request):
    """Return a value that is an empty filepath."""
    return ''

@pytest.fixture(params=[
    ' ',  # whitespace only
    '\ntext-with-newline\n',  # newline
    os.path.sep * 3  # multiple separators, each with nothing between them
])
def filepath_invalid_value(request):
    """Return a value that is a string that cannot represent a filepath."""
    return request.param
