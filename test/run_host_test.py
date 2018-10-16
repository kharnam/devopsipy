#!/usr/bin/env python3

from devopsipy import logger, host_base


def main():
    log = logger.set_logger('HostBaseTest')
    log.info('Running HostBase Test...')
    host1 = host_base.HostBase(hostname='18.232.148.79',
                               ssh_user='ec2-user',
                               ssh_key_file='/Users/kharnam/.ssh/id_rsa',
                               )
    p_lst = host1.run(commands=['uptime', 'ls -l'], print_pstate=True, print_stdout=True)
    # for p in p_lst:
    #     print(p.__str__())

    host2 = host_base.HostBase(hostname='localhost')
    p_lst = host2.run(commands=['uptime', 'ls -l'], print_pstate=True, print_stdout=True)
    # for p in p_lst:
    #     print(p.__str__())


if __name__ == '__main__':
    main()
