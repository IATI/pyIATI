"""A module containing utility functions."""
import logging
import os
from lxml import etree
import iati.core.constants


def convert_to_schema(tree):
    """Convert an etree to a schema.

    This additionally involves checking that imported schemas also work.
    """
    # TODO: surround schema conversion with error handling
    return etree.XMLSchema(tree)


def log(lvl, msg, *args, **kwargs):
    """Log a message of some level."""
    logging.basicConfig(
        filename=os.path.join(iati.core.constants.LOG_FILE_NAME),
        format='%(asctime)s %(levelname)s:%(name)s: %(message)s %(stack_info)s',
        level=logging.DEBUG
        )
    logger = logging.getLogger(iati.core.constants.LOGGER_NAME)
    logger.log(lvl, msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    """Log an error."""
    log(logging.ERROR, msg, *args, **kwargs)


def log_exception(msg, *args, **kwargs):
    """Log an exception.

    An exception is like an error, but with a stack trace.
    """
    log(logging.ERROR, msg, exc_info=True, *args, **kwargs)


def log_warning(msg, *args, **kwargs):
    """Log a warning."""
    log(logging.WARN, msg, *args, **kwargs)
