# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import logging

from bumpr.log import DRYRUN, DIFF


def test_logger_not_tty(caplog):
    logger = logging.getLogger(__name__)
    logger.debug('debug')
    logger.dryrun('dryrun')
    logger.diff('diff')
    logger.diff('+ diff')
    logger.diff('- diff')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

    assert caplog.record_tuples == [
        ('test_logging', logging.DEBUG, 'debug'),
        ('test_logging', DRYRUN, 'dryrun'),
        ('test_logging', DIFF, 'diff'),
        ('test_logging', DIFF, '+ diff'),
        ('test_logging', DIFF, '- diff'),
        ('test_logging', logging.INFO, 'info'),
        ('test_logging', logging.WARNING, 'warning'),
        ('test_logging', logging.ERROR, 'error'),
        ('test_logging', logging.CRITICAL, 'critical'),
    ]


def test_logger_tty(mocker):
    '''Ensure tty logger is working'''
    mocker.patch('bumpr.log.IS_TTY', True)
    logger = logging.getLogger(__name__)
    logger.debug('debug')
    logger.dryrun('dryrun')
    logger.diff('diff')
    logger.diff('+ diff')
    logger.diff('- diff')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
    try:
        raise Exception('An exception')
    except Exception:
        logger.exception('exception')
