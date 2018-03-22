"""A module to provide a way of locating resources within the IATI library.

The `get_*_path[s](name)` functions provide information about where to locate particular types of resources with a provided name.

Warning:
    Many of the constants in this module should be deemed private to the IATI library.

    The location of SSOT content may change. It may also require network access to perform certain tasks.

Todo:
    Determine how to distribute SSOT content - with package, or separately (being downloaded at runtime).

"""
import inspect
import os
import re
import pkg_resources
import iati.version


PACKAGE = __name__
"""The name of the resources package.

Used to locate resources when the package is distributed in certain ways that do not provide a standard filesystem.

"""

BASE_PATH = 'resources'
"""The relative location of the resources folder."""
BASE_PATH_STANDARD = os.path.join(BASE_PATH, 'standard')
"""The relative location of resources related to the IATI Standard."""
BASE_PATH_LIB_DATA = os.path.join(BASE_PATH, 'lib_data')
"""The relative location of resources not related to the IATI Standard."""
PATH_CODELISTS = 'codelists'
"""The location of the folder containing Codelists from the SSOT."""
PATH_SCHEMAS = 'schemas'
"""The location of the folder containing Schemas from the SSOT."""
PATH_RULESETS = 'rulesets'
"""The location of the folder containing Rulesets from the SSOT."""
PATH_VERSION_INDEPENDENT = 'version_independent'
"""The location of the folder containing version-independent content."""

FILE_CODELIST_EXTENSION = '.xml'
"""The expected extension of a file containing a Codelist."""
FILE_DATA_EXTENSION = '.xml'
"""The expected extension of a file containing IATI data."""
FILE_RULESET_EXTENSION = '.json'
"""The expected extension of a file containing a Ruleset."""
FILE_SCHEMA_EXTENSION = '.xsd'
"""The expected extension of a file containing a Schema."""

FILE_CODELIST_MAPPING = 'codelist-mapping'
"""The name of a file containing definitions of how Codelist values map to data."""
FILE_RULESET_SCHEMA_NAME = 'ruleset_schema'
"""The name of a file containing the Ruleset schema."""
FILE_RULESET_STANDARD_NAME = 'standard_ruleset'
"""The name of a file containing the Standard Ruleset."""
FILE_SCHEMA_ACTIVITY_NAME = 'iati-activities-schema'
"""The name of a file containing an Activity Schema."""
FILE_SCHEMA_ORGANISATION_NAME = 'iati-organisations-schema'
"""The name of a file containing an Organisation Schema."""


@iati.version.decimalise_integer
@iati.version.allow_possible_version
def get_codelist_paths(version):
    """Find the paths for all Codelists at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Codelists for.
            Decimal: Return paths for the specified version of the Standard. Includes paths for both Embedded and Non-Embedded Codelists.
            Integer: Return paths for the latest Decimal version within the given integer.
            Version-independent: Return an empty list.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Codelists at the specified version of the Standard.

    Note:
        Requesting version-independent Codelists returns an empty list rather raising a ValueError since it is planned that in the future a list of Non-Embedded Codelists will be returned.

    Todo:
        Return a list of Non-Embedded Codelists when 'version-independent' Codelists are requested.

        Look to provide an argument that allows the returned list to be restricted to only Embedded or only Non-Embedded Codelists (or both!).

    """
    paths = []

    try:
        folder_path = path_for_version(PATH_CODELISTS, version)
    except ValueError:
        folder_path = ''

    if os.path.isdir(folder_path):
        files = pkg_resources.resource_listdir(PACKAGE, folder_path[len(resource_filesystem_path('')):])
        files_codelists_only = [file_name for file_name in files if file_name[-4:] == FILE_CODELIST_EXTENSION]
        paths = [create_codelist_path(file_name, version) for file_name in files_codelists_only]

    return paths


def get_codelist_mapping_paths(version):
    """Find the paths for all Codelist Mapping files at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Codelist Mapping file for.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Codelist Mapping files at the specified version of the Standard.

    """
    return _get_paths(version, '', create_codelist_mapping_path, iati.version.STANDARD_VERSIONS_SUPPORTED)


def get_ruleset_paths(version):
    """Find the paths for all Rulesets at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Rulesets for.

    Returns:
        list(str): A list of paths to all of the Rulesets at the specified version of the Standard.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Todo:
        Consider adding is_minor() and is_major() functions in the version module.

    """
    return _get_paths(version, FILE_RULESET_STANDARD_NAME, create_ruleset_path, iati.version.STANDARD_VERSIONS_SUPPORTED)


def get_all_schema_paths(version):
    """Find the paths for all Schemas at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Schemas for.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Consider adding the IATI Codelist Schema.

    """
    return get_activity_schema_paths(version) + get_organisation_schema_paths(version)


def get_activity_schema_paths(version):
    """Find the paths for all Activity Schemas at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the activity schemas for.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Activity Schemas at the specified version of the Standard.

    """
    return _get_paths(version, FILE_SCHEMA_ACTIVITY_NAME, create_schema_path, iati.version.STANDARD_VERSIONS)


def get_organisation_schema_paths(version):  # pylint: disable=invalid-name
    """Find the paths for all Organisation Schemas at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Organisation schemas for.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Organisation Schemas at the specified version of the Standard.

    """
    return _get_paths(version, FILE_SCHEMA_ORGANISATION_NAME, create_schema_path, iati.version.STANDARD_VERSIONS)


@iati.version.allow_possible_version
def _get_paths(version, file_name, path_creation_func, supported_versions):
    """Find the paths for a component within the IATI Standard at a specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the paths for.
        file_name (str): The name of the file containing the thing of interest.
        path_creation_func (func): A function that takes a file_name and version, then returns a path.
        supported_versions (list of iati.Version): A list of minor versions that paths pointing at the thing of interest may exist for.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is of the correct type, but cannot represent a version of the IATI Standard.

    Returns:
        list(str): A list of paths to built with the given components at the specified version of the Standard.

    """
    paths = []

    try:
        # check if minor version
        if isinstance(version, iati.Version):
            versions = [version]
        elif version == iati.version.STANDARD_VERSION_ANY:
            pass  # skip to the code after the if-else
        else:
            iati.Version(version)

        versions = [version]
    except (TypeError, ValueError):
        # major version
        versions = [minor_ver for minor_ver in iati.version.versions_for_integer(int(version)) if minor_ver in supported_versions]

    try:
        num_path_creation_func_args = len(inspect.getfullargspec(path_creation_func).args)
    except AttributeError:  # python2/3 compatiblity: getfullargspec added at v3, while getargspec was deprecated
        num_path_creation_func_args = len(inspect.getargspec(path_creation_func).args)  # python2/3 compatiblity  # pylint: disable=deprecated-method

    for minor_ver in versions:
        try:
            if num_path_creation_func_args == 2:
                created_path = path_creation_func(file_name, minor_ver)
            else:
                created_path = path_creation_func(minor_ver)

            if os.path.isfile(created_path):
                paths.append(created_path)
        except ValueError:
            pass  # there is no path to check

    return paths


def create_codelist_path(codelist_name, version):
    """Determine the path of a Codelist with the given name at the specified version of the Standard.

    Args:
        codelist_name (str): The name of the codelist to locate. Should the name end in `.xml`, this shall be removed to determine the name.
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Codelists for.

    Returns:
        str: The path to a file containing the specified Codelist.

    Raises:
        TypeError: If the given Codelist name is of a type that cannot be a filepath.
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: If the given name is a string that cannot be a useful component of a filepath.
        ValueError: When a specified version is not a known version of the IATI Standard.

    Note:
        Does not check whether the specified Codelist actually exists.

    Todo:
        It needs to be determined how best to locate a user-defined Codelist that is available at a URL that needs fetching.

    """
    _ensure_portable_filepath(codelist_name)  # required for python2 compatibility

    if codelist_name[-4:] == FILE_CODELIST_EXTENSION:
        codelist_name = codelist_name[:-4]

    return path_for_version(os.path.join(PATH_CODELISTS, '{0}'.format(codelist_name) + FILE_CODELIST_EXTENSION), version)


@iati.version.decimalise_integer
def create_codelist_mapping_path(version):
    """Determine the path of the Codelist mapping file.

    version (str / int / Decimal / iati.Version): The version of the Standard to return the data files for.
        Decimal: Return a path for the specified version of the Standard.
        Integer: Return a path for the latest Decimal version within the given integer.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is not a known version of the IATI Standard.

    Returns:
        str: The path to a file containing the mapping file.

    """
    if version == iati.version.STANDARD_VERSION_ANY:
        raise ValueError('There is no Codelist mapping file that is independent of particular versions of the IATI Standard.')

    return path_for_version(FILE_CODELIST_MAPPING + FILE_CODELIST_EXTENSION, version)


def create_lib_data_path(name):
    """Determine the path of a general library data file with the given name.

    The data file is not part of the IATI Standard. It is also required in the library itself, not just for testing purposes.

    Args:
        name (str): The name of the data file to locate. The name must include the file extension.

    Returns:
        str: The path to the specified file.

    Raises:
        TypeError: If the given name is of a type that cannot be a filepath.
        ValueError: If the given name is a string that cannot be a useful component of a filepath.

    Note:
        Does not check whether the specified file actually exists.

    """
    _ensure_portable_filepath(name)  # required for python2 compatibility

    return resource_filesystem_path(os.path.join(BASE_PATH_LIB_DATA, name))


def create_ruleset_path(name, version):
    """Determine the path of a Ruleset with the given name at the specified version of the Standard.

    Args:
        name (str): The name of the Ruleset to locate.
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Ruleset for.

    Returns:
        str: The path to a file containing the specified ruleset.

    Raises:
        TypeError: If the given name is of a type that cannot be a filepath.
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: If the given name is a string that cannot be a useful component of a filepath.
        ValueError: When a specified version is not a known version of the IATI Standard.

    Note:
        Does not check whether the specified ruleset actually exists.

    Todo:
        Determine how to handle version decorators when the version argument is not first in the list. This will enable the current private function access to be removed. See #294 for more info.

    """
    version = iati.version._decimalise_integer(version)  # see todo  # pylint: disable=protected-access
    _ensure_portable_filepath(name)

    return path_for_version(os.path.join(PATH_RULESETS, '{0}'.format(name) + FILE_RULESET_EXTENSION), version)


def create_schema_path(name, version):
    """Determine the path of a Schema with the given name at the specified version of the Standard.

    Args:
        name (str): The name of the Schema to locate.
        version (str / int / Decimal / iati.Version): The version of the Standard to return the Schema for.

    Returns:
        str: The path to a file containing the specified Schema.

    Raises:
        TypeError: If the given name is of a type that cannot be a filepath.
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: If the given name is a string that cannot be a useful component of a filepath.
        ValueError: When a specified version is not a known version of the IATI Standard.

    Note:
        Does not check whether the specified Schema actually exists.

    Todo:
        Determine how to handle version decorators when the version argument is not first in the list. This will enable the current private function access to be removed. See #294 for more info.

    """
    version = iati.version._decimalise_integer(version)  # see todo  # pylint: disable=protected-access
    _ensure_portable_filepath(name)

    return path_for_version(os.path.join(PATH_SCHEMAS, '{0}'.format(name) + FILE_SCHEMA_EXTENSION), version)


@iati.version.allow_possible_version
@iati.version.normalise_decimals
def folder_name_for_version(version):
    """Return the folder name for a given version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the folder path for.

    Returns:
        str: The folder name for the specified version of the Standard.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is not a known version of the IATI Standard.

    """
    is_major = False

    if version == iati.version.STANDARD_VERSION_ANY:
        return PATH_VERSION_INDEPENDENT
    elif isinstance(version, (str, int)) and not isinstance(version, bool):
        # this logic is required since the Version class cannot currently represent Major Versions (and so have a direct `is_major` attribute - see: #265
        try:
            if str(int(version)) == str(version):
                is_major = True
        except ValueError:
            pass

    if is_major and int(version) in iati.version.STANDARD_VERSIONS_MAJOR:
        return str(version)
    elif not is_major:
        # is an iati.Version due to the `normalise_decimals` decorator
        version.patch = 0  # folder names do not currently account for patch versions

        if version in iati.version.STANDARD_VERSIONS:
            return str(version.integer) + '-0' + str(version.decimal)

    raise ValueError("Version {0} is not a known version of the IATI Standard.".format(version))


def folder_path_for_version(version):
    """Return the path for the folder containing SSOT data (schemas, codelists etc) at the specified version of the Standard.

    Args:
        version (str / int / Decimal / iati.Version): The version of the Standard to return the folder path for.

    Returns:
        str: The relative path to the folder for containing SSOT data the specified version of the Standard.

    Raises:
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: When a specified version is not a known version of the IATI Standard.

    """
    return os.path.join(BASE_PATH_STANDARD, folder_name_for_version(version))


def path_for_version(path, version):
    """Return the absolute location of a specified path at the specified version of the Standard.

    Args:
        path (str): The path to the file that is to be read in.
        version (str / int / Decimal / iati.Version): The version of the Standard to return the folder path for.

    Returns:
        str: The relative path to a file at the specified version of the Standard.

    Raises:
        TypeError: If the given path is of a type that cannot be a filepath.
        TypeError: When a specified version is of a type that cannot represent an IATI version number.
        ValueError: If the given path is a string that cannot be a useful component of a filepath.
        ValueError: When a specified version is not a known version of the IATI Standard.

    Note:
        Does not check whether anything exists at the specified path.

    """
    try:  # python2 and python3.4 compatibility
        _ensure_portable_filepath(path)
    except ValueError:
        if path != '':
            raise

    return resource_filesystem_path(os.path.join(folder_path_for_version(version), path))


def resource_filesystem_path(path):
    """Find the file system path for a specified resource path.

    Args:
        path (str): The path of the file that is to be located.

    Returns:
        str: A reference to the specified file that works however the package is distributed.

    Raises:
        TypeError: If the given path is of a type that cannot be a filepath.
        ValueError: If the given path is a string that cannot be a useful component of a filepath.

    Note:
        Does not check to see that the specified file exists.

    """
    try:
        _ensure_portable_filepath(path)
    except ValueError:
        if path != '':
            raise

    return pkg_resources.resource_filename(PACKAGE, path)


def _ensure_portable_filepath(maybe_filepath):
    """Determine whether a string could be a portable filepath.

    A portable filepath is one that meets the POSIX fully portable filename character restrictions:

    * Consists only of: A-Z a-z 0-9 . _ -
    * Does not have a leading hyphen.

    Args:
        maybe_filepath (str): A string that might be considered a valid filepath.

    Raises:
        TypeError: If the input value is of a type that cannot be a filepath.
        ValueError: If the input value is a string that cannot be a useful component of a filepath.

    Note:
        This restriction is currently tight since it's easier to tighten than loosen restrictions. The restriction could be relaxed over time.

    Todo:
        Consider utilising the Python3.4 concept of path-like objects.

    """
    if not isinstance(maybe_filepath, str):
        raise TypeError('A filesystem path must be a string. The provided value is a {0}.'.format(type(maybe_filepath)))

    path_components = maybe_filepath.split(os.path.sep)

    # allow there to be a trailing folder separator on the input maybe_filepath
    if len(path_components) > 1 and path_components[-1] == '':
        path_components.pop()

    permitted_component_regex = re.compile('^[_.A-Za-z0-9][-_.A-Za-z0-9]*$')
    for component in path_components:
        if re.match(permitted_component_regex, component) is None:
            raise ValueError('Each component in a permitted filepath must only include the following characters: A-Z a-z 0-9 . _ - (Problem component: {0} Actual path: {1})'.format(component, maybe_filepath))
