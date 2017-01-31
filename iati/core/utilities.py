"""A module containing utility functions."""
import logging
from lxml import etree


def convert_to_schema(tree):
    """Convert an etree to a schema.

    This additionally involves checking that imported schemas also work.
    """
    # TODO: surround schema conversion with error handling
    return etree.XMLSchema(tree)


def log(lvl, msg, *args, **kwargs):
    """Logs a message of some level."""
    logger = logging.getLogger('iati')
    logger.log(lvl, msg, *args, **kwargs)


def log_error(msg, *args, **kwargs):
    """Logs an error."""
    log(logging.ERROR, msg, *args, **kwargs)
