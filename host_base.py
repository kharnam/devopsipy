"""  Base Host package  """

__author__ = 'sergey kharnam'

import os
import sys

from executor import execute


class HostBase(object):
    """Class to represent basic Host functionality"""

    def __init__(self, hostname):
        hostIp = self.resolve_hostname(hostname=hostname)


    @property
    def host_info(self):
        pass

    @host_info.setter
    def host_info(self, data):
        pass

    def is_reachable(self):
        # try to reach host over ping and ssh
        pass

    def resolve_hostname(self, hostname):
        # resolve hostname and return IP
        pass

    def run(self, command):
        # execute shell command locally or over ssh
        pass

    def run_multiple(self):
        # use multi-threading and multi-processing
        pass
