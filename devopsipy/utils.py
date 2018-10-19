"""
Module to contain auxiliary functionality
"""
import yaml

__author__ = 'sergey kharnam'

import os
import inspect
import pickle
import random
import string
from pathlib import Path
import exceptions as pe

import logging
log = logging.getLogger(__name__)


def create_symlinks_to_files(**data):
    """
    Create symlinks to files.

    :param data: {link1: file1, link2:file,...}
    """
    for link, file in data.items():
        if os.path.islink(link):
            logging.debug('old symlink < {} > found. removing...'.format(file))
            os.remove(link)
        logging.debug('creating new symlink < {} > --> < {} >'.format(link, file))
        os.symlink(file, link)


def yaml_to_dic(path):
    """
    Read yaml from file and return dict
    :param file:
    :return: dict
    """
    if os.path.exists(path):
        with open(path, 'rt') as f:
            log.debug('reading yaml file --> {}'.format(path))
            log.debug('data from yaml file:\n{}'.format(yaml.safe_load(f.read())))
            return yaml.safe_load(f.read())
    else:
        raise pe.PyworkException('YAML file not found in path < {} >'.format(path))


def create_dir(dir_path):
    """
    Create directory if not exist

    :param dir_path: path
    :return:
    """
    if not os.path.exists(dir_path):
        log.debug('directory < {} > is not existing. creating...'.format(dir_path))
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        if not is_dir_exist(dir_path):
            raise Exception('directory < {} > creation failed!'.format(dir_path))
    else:
        log.debug('directory < {} > is already exist. doing nothing.'.format(dir_path))


def is_dir_exist(dir_path):
    """
    Check if directory exist

    :param dir_path: path to dir
    :return: True if exist, False otherwise
    """
    if os.path.isdir(dir_path):
        log.debug('directory < {0} > is found'.format(dir_path))
        return True
    else:
        log.debug('directory < {0} > is NOT found'.format(dir_path))
        return False


def save_data_to_file(data, file_name):
    """
    Serialize and dump data structures to file

    :param data: data
    :param file_name: path to file
    :return: none
    """
    with open(file_name, 'wb') as f:
        log.debug('dumping data to file < {} >'.format(file_name))
        log.debug(data)
        pickle.dump(data, f)


def load_data_from_file(file_name):
    """
    Fetch the original data from file
    :param file_name:
    :return: data
    """
    with open(file_name, 'rb') as f:
        data = pickle.load(f)
    log.debug('loading data from file < {} >'.format(file_name))
    log.debug(data)
    return data


def get_caller():
    """
    Function to return the name of the class and the method the function was invoked from
    :return: class and method names
    """
    stack = inspect.stack()
    class_ = stack[1][0].f_locals["self"].__class__
    method_ = stack[1][0].f_code.co_name
    return '{}.{}()'.format(str(class_), method_)


def get_random_string(length=6):
    """
    Generate random ASCII string (default: 6 chars)
    :param length: length of generated string
    :return: str
    """
    r_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    log.debug('generated random string --> {0}'.format(r_str))
    return r_str


def set_env_vars(**varibs):
    if isinstance(varibs, dict):
        for var_name, var_value in varibs.items():
            os.environ[var_name] = var_value
            log.debug('Environment variable < {0} > set to < {1} > value'.
                      format(var_name, os.environ.get(var_name, 'Not Set')))
    else:
        raise Exception('Passed variable < {0} > is not a dictionary and cannot be parsed.')


def replace_string_in_file(file_name, old_str, new_str):
    """Replaces old_str in new_str using sed.

    :param file_name: File name including path
    :type file_name: str
    :param old_str: String to be replaced
    :type old_str: str
    :param new_str: New string
    :type new_str: str
    :return None
    """
    log.debug('Replacing str "{0}" with str "{1}" in file "{2}"'.format(old_str, new_str, file_name))
    cmd = 'sed "s/{0}/{1}/g" {2} > {2}.temp && mv {2}.temp {2}'.format(old_str, new_str, file_name)
    # run(cmd, verify_rc=True)
