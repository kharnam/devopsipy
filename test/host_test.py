#!/usr/bin/env python3

import logger
import host_base


def main():
    log = logger.set_logger('HostBaseTest')
    log.info('Running HostBase Test...')
    host = host_base.HostBase(hostname='18.232.148.79', ssh_user='ec2-user', ssh_key_file='/Users/kharnam/.ssh/id_rsa')
    host.run(commands=['uptime\n', 'ls -l\n'])


if __name__ == '__main__':
    main()
