import logging
log = logging.getLogger(__name__)


def test1():
    print('\n=====  Hello from ' + __name__ + '  =====\n')
    log.info('Info test message.')
    log.debug('Debug test message.')
    log.warning('Warning test message.')
    log.error('Error test message.')
