#!/usr/bin/env python3

import logger
import host_base


def main():
    log = logger.set_logger('HostBaseTest')
    log.info('Running HostBase Test...')
    # host = host_base.HostBase(hostname='18.232.148.79',
    #                           ssh_user='ec2-user',
    #                           ssh_key_file='/Users/kharnam/.ssh/id_rsa',
    #                           )
    # p = host.run(commands=['uptime', 'ls -l'],
    #              print_pstate=True)
    # print(p.__str__())

    host = host_base.HostBase(hostname='localhost')
    p = host.run(commands=['uptime', 'ls -l'],
                 print_pstate=True)
    print(p.__str__())


if __name__ == '__main__':
    main()
