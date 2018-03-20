"""A module containing a core representation of IATI Version Numbers, plus how they are handled and compared.

Todo:
    Check whether there is any other version-related functionality to bring into this module.

    Ensure that everything in this module should be here.

"""
from decimal import Decimal
import re
import semantic_version
import iati.utilities


class Version(semantic_version.Version):
    """Representation of an IATI Standard Version Number."""

    def __init__(self, version):
        """Initialise a Version Number.

        Args:
            version (str / Decimal): A representation of an IATI version number.

        Raises:
            TypeError: If an attempt to pass something that is not a string or Decimal is made.
            ValueError: If a provided value is not a permitted version number.

        """
        if not isinstance(version, str) and not isinstance(version, Decimal):
            raise TypeError('A Version object must be created from a string or Decimal, not a {0}'.format(type(version)))

        # check to see if IATIver
        try:
            if self._is_iatidecimal(version):
                integer = str(int(version))
                decimal = str(int(version * 100) - 101)
                super(Version, self).__init__('.'.join([integer, decimal, '0']), True)
            elif self._is_iativer(version):
                integer = version.split('.')[0]
                decimal = str(int(version.split('.')[1]) - 1)
                super(Version, self).__init__('.'.join([integer, decimal, '0']), True)
            elif self._is_semver(version):
                super(Version, self).__init__(version, True)
            else:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError('A valid version number must be specified.')

    @property
    def integer(self):
        """int: The IATIver Integer Component of the Version."""
        return self.major

    @integer.setter
    def integer(self, value):
        self.major = value

    @property
    def decimal(self):
        """int: The IATIver Decimal Component of the Version.

        This differs from the minor component since it starts at .01 (1) rather than .0 (0).
        """
        return self.minor + 1

    @decimal.setter
    def decimal(self, value):
        self.minor = value

    @property
    def iativer_str(self):
        """string: An IATIver-format string representation of the Version Number.

        Note:
            The name of this property may change.
        """
        return str(self.integer) + '.0' + str(self.decimal)

    @property
    def semver_str(self):
        """string: A SemVer-format string representation of the Version Number.

        Note:
            The name of this property may change.
        """
        return '.'.join([str(self.major), str(self.minor), str(self.patch)])

    def __repr__(self):
        """str: A representation of the Version Number that will allow a copy of this object to be instantiated."""
        return "iati.Version('" + self.semver_str + "')"

    def __str__(self):
        """str: A representation of the Version Number as would exist on the Version Codelist.

        Warning:
            At present this always results in an IATIver string. This may change should SemVer be adopted.
            The helper methods must be used if a specific format is required.
        """
        return self.iativer_str

    def _is_iatidecimal(self, version):
        """Determine whether a version string is a Decimal and is a permitted value.

        Args:
            version (string or Decimal): The value to check conformance of.

        Returns:
            bool: True if the provided string is a permitted in IATIver-format version number. False if not.

        """
        if not isinstance(version, Decimal):
            return False

        valid_values = [Decimal('1.0' + str(val)) for val in range(1, 10)]

        return version in valid_values

    def _is_iativer(self, version_string):
        """Determine whether a version string is in a IATIver format and is a permitted value.

        Args:
            version_string (string): The string to check conformance of.

        Returns:
            bool: True if the provided string is a permitted in IATIver-format version number. False if not.

        """
        # a regex for what makes a valid IATIver Version Number format string
        iativer_re = re.compile(r'^((1\.0[1-9])|(((1\d+)|([2-9](\d+)?))\.0[1-9](\d+)?))$')

        return iativer_re.match(version_string)

    def _is_semver(self, version_string):
        """Determine whether a version string is in a SemVer format and is a permitted value.

        Args:
            version_string (string): The string to check conformance of.

        Returns:
            bool: True if the provided string is a permitted in SemVer-format version number. False if not.

        """
        is_semver_format = semantic_version.validate(version_string)
        try:
            is_permitted_value = semantic_version.Version(version_string).major != 0
        except ValueError:
            return False

        return is_semver_format and is_permitted_value

    def next_major(self):
        """Obtain a Version object that represents the next version after a Major Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Major Upgrade.

        """
        next_major = super(Version, self).next_major()

        return Version(str(next_major))

    def next_minor(self):
        """Obtain a Version object that represents the next version after a Minor Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Minor Upgrade.

        """
        next_minor = super(Version, self).next_minor()

        return Version(str(next_minor))

    def next_integer(self):
        """Obtain a Version object that represents the next version after an Integer Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after an Integer Upgrade.

        """
        return self.next_major()

    def next_decimal(self):
        """Obtain a Version object that represents the next version after a Decimal Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Decimal Upgrade.

        """
        return self.next_minor()

    next_patch = property()
    """Override the parent class's function to provide the next Patch Version.

    Implementation based on https://stackoverflow.com/a/235657

    Note:
        The Error that is raised has a slightly different message than if the attribute had never existed.

    Raises:
        AttributeError: An error that indicates that this attribute does not exist.

    """


STANDARD_VERSIONS_SUPPORTED = [Version(version_iativer) for version_iativer in ['1.04', '1.05', '2.01', '2.02']]
"""Define all versions of the Standard fully supported by pyIATI."""

STANDARD_VERSIONS = [Version(version_iativer) for version_iativer in ['1.01', '1.02', '1.03']] + STANDARD_VERSIONS_SUPPORTED
"""Define all versions of the Standard.

Todo:
    This constant to be populated by the values in the Version codelist, rather than hard-coded.

    Consider if functionality should extend to working with development versions of the Standard (e.g. during an upgrade process).

"""

STANDARD_VERSION_LATEST = max(STANDARD_VERSIONS)
"""The latest version of the IATI Standard."""

STANDARD_VERSIONS_MAJOR = list(set([
    minor_version.major for minor_version in STANDARD_VERSIONS
]))
"""The major versions of the IATI Standard.

Todo:
    Change from being ints to being Version()s.

"""

STANDARD_VERSIONS_MINOR = STANDARD_VERSIONS
"""The minor versions of the IATI Standard."""


STANDARD_VERSION_ANY = '*'
"""A value to represent that something is applicable to all versions of the IATI Standard - it is version independent.

Warning:
    Assumptions should not be made as to the value of this constant other than it: `is not None`

"""


def allow_fully_supported_version(input_func):
    """Decorate function by ensuring versions are fully supported by pyIATI.

    In terms of value:
    * Valid Decimal Versions will remain unchanged.
    * Invalid Decimal Versions will cause an error to be raised.
    * Other values will cause an error to be raised.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with a fully supported iati.Version representing a Decimal Version.

    """
    def wrap_allow_fully_supported_version(*args, **kwargs):
        """Act as a wrapper to ensure a version number is a Decimal that is fully supported by pyIATI.

        Raises:
            ValueError: If the input version is not a Decimal iati.Version that pyIATI fully supports.

        """
        version = args[0]

        if not _is_fully_supported(version):
            raise ValueError('{0} is not a fully supported version of the IATI Standard in a normalised representation.'.format(repr(version)))

        return input_func(*args, **kwargs)

    return wrap_allow_fully_supported_version


def allow_known_version(input_func):
    """Decorate function by ensuring versions are Decimal Versions of IATI that pyIATI knows exists.

    In terms of value:
    * Valid Decimal Versions will remain unchanged.
    * Invalid Decimal Versions will cause an error to be raised.
    * Other values will cause an error to be raised.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with an iati.Version representing a real Decimal Version.

    """
    def wrap_allow_known_version(*args, **kwargs):
        """Act as a wrapper to ensure a version number is a Decimal that exists.

        Raises:
            ValueError: If the input version is not a known Decimal iati.Version.

        """
        version = args[0]

        if not _is_known(version):
            raise ValueError('{0} is not a known version of the IATI Standard in a normalised representation.'.format(repr(version)))

        return input_func(*args, **kwargs)

    return wrap_allow_known_version


def allow_possible_version(input_func):
    """Decorate function by ensuring values specified to represent a Version can actually do so.

    In terms of value:
    * Permitted values representing an Integer or Decimal Version in a known format will remain unchanged.
    * STANDARD_VERSION_ANY will remain unchanged, as a way of representing all versions.
    * strings, integers and Decimals with values that cannot represent a Version will cause a ValueError.
    * Values of types other than string, Decimal, integer and iati.Version will cause a TypeError.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that the return value is known to represent some IATI Version Number.

    """
    def wrap_allow_possible_version(*args, **kwargs):
        """Act as a wrapper to ensure a value represents a possible version number.

        Raises:
            TypeError: If the input version is not an iati.Version, string, Decimal or integer.
            ValueError: If the input version is a string, Decimal or Integer, but the value cannot represent a Version Number.

        """
        version = args[0]

        _prevent_non_version_representations(version)

        return input_func(*args, **kwargs)

    return wrap_allow_possible_version


def decimalise_integer(input_func):
    """Decorate function by converting input version numbers to a normalised format Decimal Version.

    In terms of value:
    * Decimal Versions will remain unchanged.
    * Integer Versions will return the latest Decimal Version within the Integer.

    In terms of type:
    * strings and Decimals will become iati.Versions.
    * iati.Versions will remain unchanged.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with a iati.Version representing a Decimal Version.

    """
    def wrap_decimalise_integer(*args, **kwargs):
        """Act as a wrapper to convert input Integer Version numbers to a normalised format Decimal Version."""
        version = _decimalise_integer(args[0])

        return input_func(version, *args[1:], **kwargs)

    return wrap_decimalise_integer


def normalise_decimals(input_func):
    """Decorate function by converting an input version into an iati.Version if a value is specified that is a permitted way to represent a Decimal Version.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with an iati.Version if a Decimal version is provided.

    """
    def wrap_standardise_decimals(*args, **kwargs):
        """Act as a wrapper to ensure a version number is an iati.Version if a Decimal version is specified."""
        version = _normalise_decimal_version(args[0])

        return input_func(version, *args[1:], **kwargs)

    return wrap_standardise_decimals


def versions_for_integer(integer):
    """Return a list containing the supported versions for the input integer version.

    Args:
        integer (int): The integer version to find the supported version for.

    Returns:
        list of iati.Version: Containing the supported versions for the input integer.

    """
    return [version for version in iati.version.STANDARD_VERSIONS if version.major == integer]


def _decimalise_integer(version):
    """Convert a version number into the most appropriate Decimal Version.

    * Integer Versions will return the latest Decimal Version within the Integer. If the Integer is invalid, returns the first Decimal that would exist in the Integer.
    * All other inputs will remain unchanged.

    Args:
        version (Any): The value to convert to a Decimal Version if it represents an Integer Version.

    Returns:
        Any: The Decimal Version of the Standard that the input version relates to, or the input unchanged.

    """
    # handle major versions
    try:
        if not isinstance(version, (int, str)) or isinstance(version, bool):
            raise TypeError
        major_version = int(version)
        if major_version in iati.version.STANDARD_VERSIONS_MAJOR:
            version = max(versions_for_integer(major_version))
        elif str(major_version) == version:  # specifying only a major component
            version = Version(str(major_version) + '.0.0')
    except (ValueError, TypeError, OverflowError):
        pass

    return version


def _is_fully_supported(version):
    """Detect whether a Version is fully supported by pyIATI.

    Args:
        version (Any): The Version to check support of.

    Returns:
        bool: True if version is a fully supported iati.Version. False in all other cases.

    """
    return version in iati.version.STANDARD_VERSIONS_SUPPORTED


def _is_known(version):
    """Detect whether a Version is a version of the Standard that pyIATI knows to exist.

    Args:
        version (iati.Version): The Version to check support of.

    Returns:
        bool: True if version is an iati.Version known by pyIATI to be a released version. False in all other cases.

    """
    return version in iati.version.STANDARD_VERSIONS


def _normalise_decimal_version(version):
    """Normalise the format of Decimal Versions.

    If the specified version is a value that can act as a Decimal Version of the IATI Standard, convert it to an iati.Version.
    Any other value will be returned as-is.

    Args:
        version (Any): A value that may be a known method to represent a Decimal Version of the IATI Standard.

    Returns:
        Any: An iati.Version if the input value represents a Decimal Version of the IATI Standard. The input version in all other cases.

    """
    try:
        version = Version(version)
    except (TypeError, ValueError):
        pass

    return version


def _prevent_non_version_representations(version):
    """Detect whether a value specified to be a Version could possibly represent a Version.

    In terms of value:
    * Permitted values representing an Integer or Decimal Version in a known format will remain unchanged.
    * STANDARD_VERSION_ANY will remain unchanged, as a way of representing all versions.
    * strings, integers and Decimals with values that cannot represent a Version will cause a ValueError.
    * Values of types other than string, Decimal, integer and iati.Version will cause a TypeError.

    Args:
        version (Any): The value to check to see whether it may represent a Version in a known manner.

    Raises:
        TypeError: If anything other than an iati.Version, string, Decimal or integer is provided.
        ValueError: If a string, Decimal or integer has a value that is not in a format that is known to represent an IATI Version Number.

    """
    if not isinstance(version, (str, Decimal, int, Version)) or isinstance(version, bool):
        raise TypeError('IATI Version Numbers may only be represented as a string, Decimal, int or iati.Version. A {0} was provided.'.format(type(version)))

    try:
        Version(version)
    except ValueError:
        try:
            if version == '0' or (not version.isdigit() and version != STANDARD_VERSION_ANY):  # accept string representations of positive numbers
                raise ValueError('{0} is not a known representation of a potential IATI Version Number'.format(version))
        except AttributeError:  # invalid decimal
            raise ValueError('Only permitted versions at major version 1 may be represented using `decimal.Decimals` - {0} is not a permitted v1.0x version.'.format(version))
    except TypeError:
        # will be an int or None or iati.Version if reaching this point
        if not isinstance(version, Version) and version < 1:
            raise ValueError('IATI Integer Versions are all positive. {0} is a non-positive number.'.format(version))

    return version
