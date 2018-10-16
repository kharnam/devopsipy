"""
Module to contain Base Host functionality
"""
import calendar
import re
import sys

__author__ = 'sergey kharnam'

import logging
log = logging.getLogger(__name__)

# stdlib
import time
import os
import socket
import platform
import subprocess
import ipaddress
from pathlib import Path

# PyPy
from retry import retry
import paramiko as pm

# Pywork
from devopsipy import pstate, exceptions as pe, host_base_const as hbc


class HostBase(object):
    """
    Class to represent basic Host functionality

    :param hostname: localhost, FQDN or IPv4/IPv6
    :param ip_family: 4 for IPv4 or 6 for IPv6
    :param ssh_user: ssh user
    :param ssh_pass: ssh password
    :param ssh_key_file: ssh private key file path
    """

    def __init__(self,
                 hostname='localhost',
                 ssh_user=None,
                 ssh_pass=None,
                 ssh_key_file=None):

        # -------------------------------
        # Host State

        self._hostname = hostname  # will become DNS resolved hostname
        self._ipaddr = hostname  # will become the actual ip after resolution
        self._ipaddr_version = None
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
        """
        Prints hostname of class object as string

        :returns: string
        """
        return self._hostname

    def __repr__(self):
        """
        repr return HostBase current State

        :returns: dict
        """
        lst = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        d = dict()
        for m in lst:
            d[m] = eval('self.{}'.format(m))
        return d

    def host_base_init(self, hostname):
        """
        Initialize Host state

        :param hostname: hostname before resolution
        """
        log.info('Start host < {} > initialization...'.format(hostname))
        self.resolve_hostname(hostname=hostname)
        if self._is_localhost:
            self._os_type = platform.system()
            self._os_version = platform.version()

        else:
            self.is_pingable()
            self.is_reachable()

    @staticmethod
    def is_valid_hostname(hostname):
        """
        Validate hostname format

        :param hostname: hostname string
        :return: True if valid, False OW
        """
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]  # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def resolve_hostname(self, hostname):
        """
        Validate and resolve hostname and update relevant state vars

        :param hostname:
        :return:
        """
        # check hostname is valid
        if not self.is_valid_hostname(hostname=hostname):
            log.exception('Invalid hostname < {} >!'.format(hostname))
            raise pe.HostGeneralError('Invalid hostname < {} >!'.format(hostname))

        # check IP is valid
        try:
            log.debug('try to resolve hostname < {} >'.format(hostname))
            ip = ipaddress.ip_address(hostname)
            self._ipaddr = hostname
            log.debug('hostname successfully resolved as IP address < {} >'.format(self._ipaddr))
            self._ipaddr_version = ip.version
            log.debug('IP version < {} >'.format(self._ipaddr_version))
            self._is_localhost = ip.is_loopback
            log.debug('is IP a loopback -- < {} >'.format(self._is_localhost))
        except ValueError as e:
            log.debug('hostname failed to be resolved as an IP address. try to verify FQDN or localhost...')
            try:
                log.debug('try to resolve hostname < {} >'.format(hostname))
                self._ipaddr = socket.gethostbyname(hostname)
                log.debug('resolved IP address -- < {} >'.format(self._ipaddr))
                ip = ipaddress.ip_address(self._ipaddr)
                self._ipaddr_version = ip.version
                log.debug('IP version < {} >'.format(self._ipaddr_version))
                self._is_localhost = ip.is_loopback
                log.debug('is IP a loopback -- < {} >'.format(self._is_localhost))
            except socket.gaierror as e:
                log.exception('Failed to resolve hostname < {} >!'.format(hostname, e))
                raise pe.HostConnectivityError('Unable to resolve < {} >'.format(hostname))

    # @retry(pe.HostConnectivityError, tries=3, delay=2)
    def is_reachable(self, __retry=False):
        """
        Test if the host is reachable by ping and ssh

        :returns: True if reachable, False OW
        """
        log.info('Verifying host < {} > is reachable over SSH...'.format(self._hostname))
        p = self.run('echo')[0]
        if p.rc:
            log.critical('SSH to < {} > failed!'.format(self._hostname))
            self._is_reachable = False
            raise pe.HostConnectivityError('Failed to SSH host < {} >'.format(self._hostname))
        self._is_reachable = True
        return self._is_reachable

    @retry(pe.HostConnectivityError, tries=3, delay=2)
    def is_pingable(self, __retry=False):
        """
        Test if the host is reachable by ping

        :returns: True if pingable, False OW
        """
        log.info('Verifying host < {} > is pingable...'.format(self._hostname))
        rc = os.system("ping -c 1 -W2 " + self._hostname + " > /dev/null 2>&1")
        if rc == 0:
            log.info('Host < {} > pinged successfully'.format(self._hostname))
            self._is_pingable = True
            return self._is_pingable
        else:
            log.warning('Failed to ping host < {} >'.format(self._hostname))
            self._is_pingable = False
            if __retry:
                raise pe.HostConnectivityError('Failed to ping host < {} >'.format(self._hostname))
            else:
                return self._is_pingable

    # -------------------------------
    # Host Actions

    @retry(Exception, tries=2, delay=2)
    def run(self, commands,
            blocking=True,
            timeout=0,
            ssh_timeout=0,
            verify_rc=False,
            print_stdout=False,
            print_pstate=False):
        """
        Execute shell command:
        - remote host -- over SSH
        - localhost -- over subprocess

        :param commands:
        :param blocking:
        :param timeout:
        :param ssh_timeout:
        :param verify_rc:
        :param pid:
        :param print_stdout:
        :param print_pstate:
        :return: list of pstate objects (to support multiple commands in one session)
        """

        p_lst = list()
        if not self._is_localhost:
            client = self.__get_ssh_client(timeout=ssh_timeout)
            if isinstance(commands, str):
                commands = commands.split()
            for cmd in commands:
                p = pstate.Pstate(hostname=self._hostname)
                p.ipaddr = self._ipaddr
                log.debug('executing command --> {}'.format(cmd))
                p.epoch = calendar.timegm(time.gmtime())
                start = time.time()
                stdin, stdout, stderr = client.exec_command(cmd)
                p.runtime = time.time() - start
                p.cmd = cmd
                p.stdout = stdout.read().decode(encoding='UTF-8')
                p.stderr = stderr.read().decode(encoding='UTF-8')
                p.rc = stdout.channel.recv_exit_status()

                p_lst.append(p)
                if print_pstate:
                    log.info('PSTATE:\n{}'.format(p.__str__()))

            client.close()
        else:
            for cmd in commands:
                p = pstate.Pstate(hostname=self._hostname)
                p.ipaddr = self._ipaddr
                log.debug('executing command --> {}'.format(cmd))
                p.epoch = calendar.timegm(time.gmtime())
                start = time.time()
                prc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.pid = prc.pid
                p.cmd = cmd
                p.rc = prc.returncode
                # This should allow background (non blocking) execution !!!
                # It's the caller's responsibility to call process.wait()
                if not blocking:
                    return prc

                if prc.stdout:
                    while True:
                        line = prc.stdout.readline().decode(encoding='UTF-8')
                        # print line to screen
                        if print_stdout:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                        if not line:
                            break
                        p.stdout.append(line.rstrip())

                if prc.stderr:
                    while True:
                        line = prc.stderr.readline().decode(encoding='UTF-8')
                        # print line to screen
                        if print_stdout:
                            sys.stdout.write(line)
                            sys.stdout.flush()
                        if not line:
                            break
                        p.stderr.append(line.rstrip())
                prc.wait()
                p.runtime = time.time() - start

                p_lst.append(p)
                if print_pstate:
                    log.info('PSTATE:\n{}'.format(p.__str__()))

        return p_lst

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
