"""
Module to implement logging facility for Pywork framework

Usage:
In __main__:
log = logger.set_logger('<logger name>')

In modules:
import logging
log = logging.getLogger(__name__)

"""

__author__ = 'sergey kharnam'


import os
import logger_const as lc
import utils as pu
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import time
import yaml
import ctypes

log_dir_path = str()
logger_name = str()
log_file_info = str()
log_file_error = str()
log_file_debug = str()


# -----------------------------------------
# Logger setup

def set_logger(
        lgr_name,
        default_path=lc.LOG_DEFAULT_CONFIG_PATH,
        default_level='DEBUG',
        env_key='LOG_CFG'):
    """
    Setup logging configuration

    :param lgr_name: logger name
    :param default_path: path to logger conf file
    :param default_level: default log level
    :param env_key: set logger conf from env var
    :return: configured logger
    """
    # handling paths and files
    _set_log_file_names_and_paths(lgr_name=lgr_name)
    path = default_path
    value = os.getenv(env_key, None)

    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    return logging.getLogger(lgr_name)


# TODO: implement formatter_on() to back to default (or arbitrary) formatter
def formatter_off():
    f = logging.Formatter(fmt='%(message)s', style='%', datefmt='%Y-%m-%d %H:%M:%S')
    for h in logging.getLogger().handlers:
        h.setFormatter(f)


def _set_log_file_names_and_paths(lgr_name):
    symlink_dict = dict()
    global logger_name
    logger_name = lgr_name + '_' + time.strftime("%Y%m%d_%H%M%S")
    global log_dir_path
    log_dir_path = lc.LOG_DIR_BASE + logger_name
    global log_file_info
    log_file_info = log_dir_path + '/' + logger_name + lc.LOG_FILE_EXTENSION_INFO
    symlink_dict[lc.LOG_FILE_SYMLINK_INFO] = log_file_info
    global log_file_error
    log_file_error = log_dir_path + '/' + logger_name + lc.LOG_FILE_EXTENSION_ERROR
    symlink_dict[lc.LOG_FILE_SYMLINK_ERROR] = log_file_error
    global log_file_debug
    log_file_debug = log_dir_path + '/' + logger_name + lc.LOG_FILE_EXTENSION_DEBUG
    symlink_dict[lc.LOG_FILE_SYMLINK_DEBUG] = log_file_debug

    pu.create_dir(log_dir_path)
    pu.create_symlinks_to_files(**symlink_dict)


# -----------------------------------------
# Log handlers

class FileHandlerDebug(RotatingFileHandler):
    """
    Class to extend original logging.RotatingFileHandler functionality
    This handler is responsible to handle DEBUG, INFO, WARNING, ERROR and CRITICAL levels
    Output to log file only
    """

    def __init__(self, max_bytes, backup_count):
        super().__init__(filename=log_file_debug,
                         maxBytes=max_bytes,
                         backupCount=backup_count)


class FileHandlerInfo(RotatingFileHandler):
    """
    Class to extend original logging.RotatingFileHandler functionality
    This handler is responsible to handle INFO, WARNING, ERROR and CRITICAL levels
    Output to console and to log files
    """

    def __init__(self, max_bytes, backup_count):
        super().__init__(filename=log_file_info,
                         maxBytes=max_bytes,
                         backupCount=backup_count)


class FileHandlerError(RotatingFileHandler):
    """
    Class to extend original logging.FileHandler functionality
    This handler is responsible to handle only ERROR and CRITICAL levels
    Output to console and to log files
    """

    def __init__(self, max_bytes, backup_count):
        super().__init__(filename=log_file_error,
                         maxBytes=max_bytes,
                         backupCount=backup_count)


class ColorizingStreamHandler(logging.StreamHandler):
    """
    Colorize TTY output
    """
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    # levels to (background, foreground, bold/intense)
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
        }
    else:
        level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,  # black
            1: 0x04,  # red
            2: 0x02,  # green
            3: 0x06,  # yellow
            4: 0x01,  # blue
            5: 0x05,  # magenta
            6: 0x03,  # cyan
            7: 0x07,  # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2):  # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08  # foreground intensity on
                            elif p == 0:  # reset to default color
                                color = 0x07
                            else:
                                pass  # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message
