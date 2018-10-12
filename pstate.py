"""
Module to contain 'process state' object (pstate) related functionality
"""

__author__ = 'sergey kharnam'


class Pstate(object):
    """
    Class to represent process state (pstate) object data store
    pstate contains:
    - hostname (str) -- hostname of execution machine
    - rc (int) -- return code (default: -1)
    - pid (str) -- process id
    - epoch (int) -- start of exec timestamp
    - runtime (float) -- time took to exec cmd
    - cmd (str) -- executed cmd
    - stdout (list) -- stdout
    - stderr (list)` -- stderr
    """

    def __init__(self, rc=-1, hostname='unknown'):
        """
        Function to initialize pstate class

        :param rc: default return code
        :type rc: int
        :param hostname: hostname the command was executed from
        :type hostname: str
        :returns: None
        """
        self.hostname = hostname
        self.rc = rc
        self.pid = None
        self.epoch = None
        self.runtime = 0.0
        self.cmd = str()
        self.stdout = list()
        self.stderr = list()

    @property
    def success(self):
        """
        Getter property returning boolean value indicating success
        """
        return not self.rc

    def __repr__(self):
        """
        Function to display the pstate return code of the executed command
        """
        return "<pstate RC: {0}>".format(self.rc)

    def __str__(self):
        """
        Returns pstate fields: stdout, stderr, cmd, rc, runtime, epoch, pid and hostname

        :param: None
        :returns: stdout, stderr, cmd, rc, runtime, epoch, pid  and hostname
        :rtype: str
        """
        pstate_data = [
            "CMD: " + self.cmd,
            "RC: " + str(self.rc),
            "EPOCH: " + str(self.epoch),
            "PID: " + str(self.pid),
            "HOST: " + self.hostname,
            "RUNTIME: " + str(self.runtime),
            "STDOUT: " + str(self.stdout),
            "STDERR: " + str(self.stderr)
        ]
        return '\n' + '\n'.join(pstate_data) + '\n'
