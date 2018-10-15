"""
Module to contain logger related constants
"""
__author__ = 'sergey kharnam'

LOG_DIR_BASE = '/tmp/logs/'
LOG_FILE_EXTENSION_INFO = '.info.log'
LOG_FILE_EXTENSION_ERROR = '.error.log'
LOG_FILE_EXTENSION_DEBUG = '.debug.log'
LOG_FILE_SYMLINK_INFO = LOG_DIR_BASE + 'latest.info'
LOG_FILE_SYMLINK_ERROR = LOG_DIR_BASE + 'latest.error'
LOG_FILE_SYMLINK_DEBUG = LOG_DIR_BASE + 'latest.debug'

LOG_ENV_VAR_NAME = 'LOG_CFG'
LOG_DEFAULT_CONFIG_PATH = './logger.yml'
