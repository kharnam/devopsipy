"""
Module to contain Base Host functionality
"""
import calendar
import sys

__author__ = 'sergey kharnam'

import logging
log = logging.getLogger(__name__)

import pstate
import time
import os
import socket
import platform
import subprocess
from pathlib import Path
import pywork_exceptions as pe
import pywork_decorators as pd
import host_base_const as hbc
import paramiko as pm


class HostBase(object):
    """Class to represent basic Host functionality"""

    def __init__(self,
                 hostname='localhost',
                 ssh_user=None,
                 ssh_pass=None,
                 ssh_key_file=None):

        # -------------------------------
        # Host State

        self._hostname = hostname  # will become DNS resolved hostname
        self._ipaddr = hostname  # will become the actual ip after resolution
        self._is_localhost = None
        self._ssh_pass = ssh_pass
        self._ssh_user = ssh_user
        self._ssh_key_file = ssh_key_file
        self._os_type = None
        self._os_version = None
        self._is_pingable = None
        self._is_reachable = None

        self.host_base_init(hostname=hostname)

    # -------------------------------
    # Host State Functions

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

    def host_base_init(self, hostname):
        """
        Initialize Host state

        :param hostname: hostname before resolution
        """
        self._is_localhost()
        if hostname == 'localhost':
            self.resolve_hostname(hostname)
            log.debug('hostname -- < {} >'.format(hostname))
            self.update_host_info()
        else:
            self.resolve_hostname(hostname)
            log.debug('hostname -- < {} >'.format(hostname))
            self.update_host_info()
            self.is_reachable()

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
        """
        Setter for os_type

        :param value: new value to set to
        :type value: str
        :returns: None
        """
        self._os_type = value

    def update_host_info(self):
        """
        Updates host OS type and version

        :Parameters: none
        :return: None
        """

        self._os_type = platform.system()
        self._os_version = platform.version()

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

    def is_pingable(self, pingretry=3):
        """
        Test if the host is reachable by ping

        :returns: True if pingable, False OW
        """

        for i in range(pingretry):
            p = os.system('ping -c 1 -w 1 {} &>/dev/null'.format(self._ipaddr))
            if p:
                log.debug('ping to {0} failed with exit code {1}'.format(self._hostname, p))
                if i != pingretry - 1:  # skip sleep if on last ping
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
            log.debug('try to resolve hostname < {} >'.format(hostname))
            self._ipaddr = socket.gethostbyname(hostname)
            log.debug('resolved IP address -- < {} >'.format(self._ipaddr))
            self._hostname = socket.gethostbyaddr(hostname)[0]
            log.debug('resolved hostname -- < {} >'.format(self._hostname))
        except socket.gaierror as e:
            log.exception('Failed to resolve hostname < {} >!'.format(hostname, e))
            raise pe.HostConnectivityError('Unable to resolve < {} >'.format(hostname))





















    # -------------------------------
    # Host Actions

    # TODO: implement retry
    def run(self, commands,
            blocking=True,
            timeout=0,
            ssh_timeout=0,
            verify_rc=False,
            deque=None,
            pid=None,
            print_stdout=False,
            print_pstate=False):

        p = pstate.Pstate(hostname=self._hostname)
        p.ipaddr = self._ipaddr

        if not self._is_localhost:
            client = self.__get_ssh_client(timeout=ssh_timeout)
            for cmd in commands:
                log.debug('executing command --> {}'.format(cmd))
                p.epoch = calendar.timegm(time.gmtime())
                start = time.time()
                stdin, stdout, stderr = client.exec_command(cmd)
                p.runtime = time.time() - start
                p.cmd = cmd
                p.stdout = stdout.read()
                p.stderr = stderr.read()
                p.rc = stdout.channel.recv_exit_status()

                if print_pstate:
                    log.info('PSTATE:\n{}'.format(p.__str__()))

            client.close()
        else:
            for cmd in commands:
                log.debug('executing command --> {}'.format(cmd))
                p.epoch = calendar.timegm(time.gmtime())
                start = time.time()
                prc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.pid = prc.pid
                p.cmd = cmd
                # This should allow background (non blocking) execution !!!
                # It's the caller's responsibility to call process.wait()
                if not blocking:
                    return prc

                if prc.stdout is not None:
                    while True:
                        line = prc.stdout.readline()
                        # print line to screen
                        if print_stdout:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                        if not line:
                            break
                        p.stdout.append(line.rstrip())
                    prc.wait()
                else:
                    # Get stdout, stderr and rc
                    try:
                        prc_stdout, prc_stderr = prc.communicate()
                    except Exception as e:
                        # if we got an exception it probably means we were killed from the outside, so force rc=0
                        log.exception('Exception during subprocess.Popen communicate()\n{}'.format(e))
                        raise pe.HostCommandExecutionError('Exception during subprocess.Popen communicate()\n{}'
                                                           .format(e))
                    p.runtime = time.time() - start
                    p.rc = prc.returncode
                    if print_pstate:
                        log.info('PSTATE:\n{}'.format(p.__str__()))
        return p


                # # Handle stdout and stderr
                # if stdout or deque is not None:
                #     p.stderr = [l.rstrip() for l in prc.stderr.read().split('\n')]
                # else:
                #     p.stdout = [l.rstrip() for l in prc_stdout.split('\n')]
                #     p.stderr = [l.rstrip() for l in prc_stderr.split('\n')]
                #
                # if p.stdout and not p.stdout[-1]:
                #     p.stdout = p.stdout[:-1]
                #
                # if p.stderr and not p.stderr[-1]:
                #     p.stderr = p.stderr[:-1]








    def __get_ssh_client(self, timeout=10):
        """
        Return paramiko.SSHClient object after establishing authentication
        :return: paramiko.SSHClient
        """

        client = pm.SSHClient()
        log.info('SSHing to < {} >'.format(self._hostname))
        if self._ssh_key_file and Path(self._ssh_key_file).is_file():
            log.info('Try to connect with private key < {} >'.format(self._ssh_key_file))
            try:
                log.debug('loading private key from file...')
                key = pm.RSAKey.from_private_key_file(self._ssh_key_file)
                client.load_system_host_keys()
                log.debug('adding path to known hosts file...')
                client.load_host_keys(os.path.expanduser(hbc.FILE_KNOWN_HOSTS))
                log.debug('setting missing host policy')
                client.set_missing_host_key_policy(AllowAllKeys())
                log.debug('trying to connect with client...')
                client.connect(self._hostname, username=self._ssh_user, pkey=key)
            except Exception as e:
                log.exception('Failed to connect with private key!\n{}'.format(e))
                # try to connect with user/password
                if self._ssh_user and self._ssh_pass:
                    log.info('Try to connect with user < {} > and password < {} >'
                             .format(self._ssh_user, self._ssh_pass))
                    # TODO: timeout=timeout cause "[Errno 36] Operation now in progress" problem
                    client.connect(self._hostname, username=self._ssh_user, password=self._ssh_pass)
                else:
                    log.error('SSH user and password are not set!')
                    raise pe.HostConnectivityError('Unable to connect host < {} >'.format(self._hostname))
        return client


class AllowAllKeys(pm.WarningPolicy):
    def missing_host_key(self, client, hostname, key):
        return
