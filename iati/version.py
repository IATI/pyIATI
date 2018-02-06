"""A module containing components that describe the IATI Standard itself (rather than the parts it is made up of)."""
from decimal import Decimal
import re
import semantic_version
# try-except to prevent errors caused by `from .versions import Version` in `__init__.py`
try:
    import iati
    iati.Version  # pylint: disable=pointless-statement
    import iati.constants
except AttributeError:
    pass
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
        """int: The IATIver Decimal Component of the Version."""
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


def convert_to_decimal(input_func):
    """Decorate function by converting input version numbers to a standardised format Decimal Version.

    In terms of value:
    * Decimal Versions will remain unchanged.
    * Integer Versions will return the latest Decimal Version within the Integer.

    In terms of type:
    * strings and Decimals will become iati.Versions.
    * iati.Versions will remain unchanged.

    Errors may be raised:
    * Invalid types will cause a TypeError
    * Invalid values will cause a ValueError

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with a iati.Version representing a Decimal Version.

    """
    def wrapper(*args, **kwargs):
        """Act as a wrapper to convert input version numbers to a standardised format Decimal Version.

        Raises:
            TypeError: When a version is of a type that cannot be converted to a version of the IATI Standard.
            ValueError: When a specified version of the correct type cannot be converted to a version of the IATI Standard.

        """
        version = _specific_version_for(args[0])

        return input_func(version, *args[1:], **kwargs)

    return wrapper


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
    def wrapper(*args, **kwargs):
        """Act as a wrapper to ensure a version number is a Decimal that is fully supported by pyIATI.

        Raises:
            TypeError: If the input version is not an iati.Version.
            ValueError: If the input version is not a Decimal Version that pyIATI fully supports.

        """
        version = args[0]

        if not _is_fully_supported(version):
            raise ValueError('Version {0} is not a valid version of the IATI Standard.'.format(version))

        return input_func(*args, **kwargs)

    return wrapper


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
    def wrapper(*args, **kwargs):
        """Act as a wrapper to ensure a version number is a Decimal that exists.

        Raises:
            TypeError: If the input version is not an iati.Version.
            ValueError: If the input version is not a known Decimal Version.

        """
        version = args[0]

        if not _is_known(version):
            raise ValueError('Version {0} is not a valid version of the IATI Standard.'.format(version))

        return input_func(*args, **kwargs)

    return wrapper


def standardise_decimals(input_func):
    """Decorate function by converting an input version into an iati.Version if a value is specified that is a permitted way to represent a Decimal Version.

    Args:
        input_func (function): The function to decorate. Takes the `version` argument as its first argument.

    Returns:
        function: The input function, wrapped such that it is called with an iati.Version if a Decimal version is provided.

    """
    def wrapper(*args, **kwargs):
        """Act as a wrapper to ensure a version number is an iati.Version if a Decimal version is specified."""
        version = _standardise_decimal_version(args[0])

        return input_func(version, *args[1:], **kwargs)

    return wrapper


def _is_fully_supported(version):
    """Detect whether a Version is fully supported by pyIATI.

    Args:
        version (iati.Version): The Version to check support of.

    Returns:
        bool: True if the Version is fully supported. False if the Version is not fully supported.

    Raises:
        TypeError: If anything other than an iati.Version is provided.

    """
    if not isinstance(version, Version):
        raise TypeError('The version must be provided as an iati.Version')

    return version in iati.constants.STANDARD_VERSIONS_SUPPORTED


def _is_known(version):
    """Detect whether a Version is a version of the Standard that pyIATI knows to exist.

    Args:
        version (iati.Version): The Version to check support of.

    Returns:
        bool: True if the Version is known by pyIATI. False if the Version is not known.

    Raises:
        TypeError: If anything other than an iati.Version is provided.

    """
    if not isinstance(version, Version):
        raise TypeError('The version must be provided as an iati.Version')

    return version in iati.constants.STANDARD_VERSIONS


@standardise_decimals
def _specific_version_for(version):
    """Convert a version number into the most appropriate Decimal Version.

    * Decimal Versions will remain unchanged.
    * Integer Versions will return the latest Decimal Version within the Integer. If the Integer is invalid, returns the first Decimal that would exist in the Integer.

    Args:
        version (str / Decimal / iati.Version): The version to obtain a specific version for.

    Raises:
        TypeError: When a version is of a type that cannot be converted to a version of the IATI Standard.
        ValueError: When a specified version of the correct type cannot be converted to a version of the IATI Standard.

    Returns:
        str: The Decimal Version of the Standard that the input version relates to.

    """
    # handle major versions
    try:
        if version in [True, False] or isinstance(version, Decimal):
            raise TypeError
        major_version = int(version)
        if major_version in iati.constants.STANDARD_VERSIONS_MAJOR:
            version = max(iati.utilities.versions_for_integer(major_version))
        elif str(major_version) == version:  # specifying only a major component
            version = Version(str(major_version) + '.0.0')
    except (ValueError, TypeError, OverflowError):
        pass

    if isinstance(version, Version):
        return version
    elif isinstance(version, Decimal):
        raise ValueError
    elif version is None:
        raise ValueError

    raise ValueError


def _standardise_decimal_version(version):
    """Standardise the format of Decimal Versions.

    If the specified version is a value that can act as a Decimal Version of the IATI Standard, convert it to an iati.Version.
    Any other value will be returned as-is.

    Args:
        version (Any): A value that may be a known method to represent a Decimal Version of the IATI Standard.

    Returns:
        Any: An iati.Version if the input value represents a Decimal Version of the IATI Standard. The input version in all other cases.

    """
    try:
        version = iati.Version(version)
    except (TypeError, ValueError):
        pass

    return version
