# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

__all__ = (
    'init'
)

import os
import sys
import logging

from logging import Formatter, StreamHandler, DEBUG, INFO

RESET_TERM = '\033[0;m'

COLOR_CODES = {
    'red': 31,
    'yellow': 33,
    'cyan': 36,
    'white': 37,
    'bgred': 41,
    'bggrey': 100,
}

LEVEL_COLORS = {
    'DEBUG': 'bggrey',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bgred',
}


def ansi(color, text):
    """Wrap text in an ansi escape sequence"""
    code = COLOR_CODES[color]
    return '\033[1;{0}m{1}{2}'.format(code, text, RESET_TERM)


class ANSIFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into colored text, using ANSI
    escape sequences.
    """
    def format(self, record):
        msg = record.getMessage()
        if record.levelname == 'INFO':
            return ansi('cyan', '-> ') + msg
        else:
            color = LEVEL_COLORS.get(record.levelname, 'white')
            return ansi(color, record.levelname) + ': ' + msg


class TextFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into text.
    """
    def format(self, record):
        if not record.levelname or record.levelname == 'INFO':
            return record.getMessage()
        else:
            return record.levelname + ': ' + record.getMessage()


def init(level=INFO):
    logger = logging.getLogger()
    handler = StreamHandler()

    if (os.isatty(sys.stdout.fileno()) and not sys.platform.startswith('win')):
        fmt = ANSIFormatter()
    else:
        fmt = TextFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)


if __name__ == '__main__':
    init(level=DEBUG)

    root_logger = logging.getLogger()
    root_logger.debug('debug')
    root_logger.info('info')
    root_logger.warning('warning')
    root_logger.error('error')
    root_logger.critical('critical')
