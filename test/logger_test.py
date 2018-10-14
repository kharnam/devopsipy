#!/usr/bin/env python3

import logger_test_1
import logger_test_2
import logger


def main():
    log = logger.set_logger('TEST')
    log.info('Info test message.')
    log.debug('Debug test message.')
    log.warning('Warning test message.')
    log.error('Error test message.')
    try:
        1/0
    except ZeroDivisionError as e:
        log.exception('Exception test message: {}'.format(e))

    logger_test_1.test1()
    logger_test_2.test2()
    print('\n=====  Log meta-data off  =====\n')
    logger.formatter_off()
    log.info('Info test message.')
    log.debug('Debug test message.')
    log.warning('Warning test message.')
    log.error('Error test message.')
    try:
        1/0
    except ZeroDivisionError as e:
        log.exception('Exception test message: {}'.format(e))


if __name__ == '__main__':
    main()
