"""
Module to contain Pywork exceptions
"""

__author__ = 'sergey kharnam'

import logging
log = logging.getLogger(__name__)


class PyworkException(Exception):
    """
    Represents generic exception with custom message
    """
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
        log.exception(message)
