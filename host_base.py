"""
Module to contain Base Host functionality
"""

__author__ = 'sergey kharnam'

import time
import os
import sys
import socket
import platform
import pywork_exceptions as pe
import paramiko as pm

import logging
log = logging.getLogger(__name__)


class HostBase(object):
    """Class to represent basic Host functionality"""

    def __init__(self, ssh_user=None, ssh_pass=None, ssh_priv_key_file=None, hostname='localhost',
                 expect_reachable=True):
        self._hostname = hostname  # will become DNS resolved hostname
        self._ipaddr = hostname  # will become the actual ip after resolution
        self._is_localhost = None
        self._pingretry = 3
        self._ssh_pass = ssh_pass
        self._ssh_user = ssh_user
        self._ssh_priv_key_file = ssh_priv_key_file
        self._os_type = None
        self._os_version = None
        self._is_pingable = None
        self._is_reachable = None

        self.host_base_init(hostname=hostname)

    def host_base_init(self, hostname):
        self.resolve_hostname(hostname)
        self.update_host_info()
        # self.is_reachable()

    @property
    def os_version(self):
        """Getter for os_version

        :Parameters: none
        :return: version of OS
        :rtype: str
        """
        if self._os_version is None:
            self.update_host_info()
        return self._os_version

    @os_version.setter
    def os_version(self, value):
        """Setter for os_version

        :param value: new value to set to
        :type value: str
        :returns: None"""
        self._os_version = value

    @property
    def os_type(self):
        """Getter for os_type

        :Parameters: none
        :return: type of OS
        :rtype: str
        """
        if self._os_type is None:
            self.update_host_info()
        return self._os_type

    @os_type.setter
    def os_type(self, value):
        """Setter for os_type

        :param value: new value to set to
        :type value: str
        :returns: None
        """
        self._os_type = value

    def update_host_info(self):
        """Updates host OS type and version

        :Parameters: none
        :return: None
        """

        self._os_type = platform.system()
        self._os_version = platform.version()

    def __str__(self):
        """Prints hostname of class object as string

           :Parameters: none
           :returns: string
        """
        return self._hostname

    def __repr__(self):
        """repr return hostname of class object as string

           :Parameters: none
           :returns: string
        """
        return self._hostname

    def is_localhost(self):
        """
        Detect if provided host is a localhost

        :return: True if localhost, False OW
        """
        log.debug('hostname is < {} >'.format(self._hostname))
        if self._hostname == 'localhost' or self._ipaddr == '127.0.0.1':
            self._is_localhost = True
        else:
            self._is_localhost = False
        log.debug('_is_localhost = < {} >'.format(self._is_localhost))
        return self._is_localhost

    def is_reachable(self):
        """
        Test if the host is reachable by ping and ssh

        :returns: True if reachable, False OW
        """
        if not self.is_pingable():
            self._is_reachable = False
            return self._is_reachable
        else:
            # if ping succeeds, test ssh
            # TODO: implement run()
            rc = self.run('echo', timeout=5)
            if rc:
                log.debug('ssh to %s did not return for 5 seconds'.format(self._hostname))
                self._is_reachable = False
                return self._is_reachable
        self._is_reachable = True
        return self._is_reachable

    def is_pingable(self):
        """
        Test if the host is reachable by ping

        :returns: True if pingable, False OW
        """

        for i in range(self._pingretry):
            p = os.system('ping -c 1 -w 1 {} &>/dev/null'.format(self._ipaddr))
            if p:
                log.debug('ping to {0} failed with exit code {1}'.format(self._hostname, p))
                if i != self._pingretry - 1:  # skip sleep if on last ping
                    time.sleep(2)  # wait 2 seconds before next ping
            else:
                return True
        return False

    def resolve_hostname(self, hostname):
        """
        Resolve hostname and return IP

        :param hostname:
        :return:
        """

        try:
            log.info('trying to resolve hostname < {} >'.format(hostname))
            self._ipaddr = socket.gethostbyname(hostname.strip())
            self._hostname = hostname
        except socket.gaierror as e:
            log.exception('Failed to resolve hostname < {} >'.format(hostname))

    def run(self, cmd, sudo=False, capture=True, timeout=10):
        # execute shell command locally or over ssh
        if self.is_localhost():
            p = execute(cmd, capture=capture, sudo=sudo)  # , timeout=timeout)
            log.info(p)
        else:
            cmd = RemoteCommand(self._ipaddr, cmd, capture=True)
            rc = cmd.start()
            log.debug(cmd.output)

    def run_multiple(self):
        # use multi-threading and multi-processing
        pass
