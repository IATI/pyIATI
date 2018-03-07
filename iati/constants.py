"""A module containing constants required throughout IATI library code.

The contents of this file are not designed to be user-editable. Only edit if you know what you are doing!

Warning:
    This contents of this module should currently be deemed private.

Todo:
    Allow logging constants to be user-definable.

"""

LOG_FILE_NAME = 'iatilib.log'
"""The location of the primary IATI log file.

Warning:
    Logging should be clearly user-definable.

"""
LOGGER_NAME = 'iati'
"""The name of the primary IATI Logger.

Warning:
    This should be better based on specific packages.

"""

NAMESPACE = '{http://www.w3.org/2001/XMLSchema}'
"""The namespace that IATI Schema XSD files are specified within."""
NSMAP = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
"""A dictionary for interpreting namespaces in IATI Schemas."""
