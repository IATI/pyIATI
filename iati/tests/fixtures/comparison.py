"""Pytest fixtures for comparing values."""
import pytest

_CMP_FUNC_EQUAL_VAL = [
    lambda x, y: x == y,
    lambda x, y: y == x
]


_CMP_FUNC_EQUAL_HASH = [
    lambda x, y: hash(x) == hash(y)
]


_CMP_FUNC_DIFFERENT_VAL = [
    lambda x, y: x != y,
    lambda x, y: y != x
]


_CMP_FUNC_DIFFERENT_HASH = [
    lambda x, y: hash(x) != hash(y)
]


@pytest.fixture(params=_CMP_FUNC_EQUAL_VAL)
def cmp_func_equal_val(request):
    """Return a comparison function that checks whether two values are equal."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_EQUAL_HASH)
def cmp_func_equal_hash(request):
    """Return a comparison function that checks whether two values have the same hash."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_EQUAL_VAL + _CMP_FUNC_EQUAL_HASH)
def cmp_func_equal_val_and_hash(request):
    """Return a comparison function that checks whether two values are equal and have the same hash."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_VAL)
def cmp_func_different_val(request):
    """Return a comparison function that checks whether two values are different."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_HASH)
def cmp_func_different_hash(request):
    """Return a comparison function that checks whether two hashes are different."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_VAL + _CMP_FUNC_DIFFERENT_HASH)
def cmp_func_different_val_and_hash(request):
    """Return a comparison function that checks whether two values are different and have different hashes."""
    return request.param
