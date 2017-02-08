"""A module containing constants required throughout IATI library code.

Todo:
    Allow logging constants to be user-definable.
"""


LOG_FILE_NAME = 'iatilib.log'
"""The location of the primary IATI log file."""
LOGGER_NAME = 'iati'
"""The name of the primary IATI Logger."""
NAMESPACE = '{http://www.w3.org/2001/XMLSchema}'
"""The namespace that IATI Schema XSD files are specified within."""
NSMAP = {'xsd': 'http://www.w3.org/2001/XMLSchema'}
"""A dictionary for interpreting namespaces in IATI Schemas."""
