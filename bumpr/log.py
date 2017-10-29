# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import sys
import logging

import click

from bumpr.utils import color, yellow, green, red, cyan, white, magenta, ARROW, DEBUG

DRYRUN = 25
DIFF = 15

LEVEL_COLORS = {
    logging.DEBUG: cyan,
    logging.WARNING: yellow,
    logging.ERROR: red,
    logging.CRITICAL: color('black', bg='red', bold=True),
}

IS_TTY = os.isatty(sys.stdout.fileno()) and not sys.platform.startswith('win')


def format_multiline(string):
    string = '\n  └ '.join(string.splitlines())
    string = string.replace('└', '│', (string.count('└') - 1))
    return '  │ {0}'.format(string)


def replace_last(string, char, replacement):
    return replacement.join(string.rsplit(char, 1))


class CliFormatter(logging.Formatter):
    """
    Convert a `logging.LogRecord' object into colored text, using ANSI
    escape sequences.
    """
    def format(self, record):
        if not IS_TTY:
            return super(CliFormatter, self).format(record)
        if record.levelno == DIFF:
            if record.msg.startswith('+'):
                record.msg = green(record.msg)
            elif record.msg.startswith('-'):
                record.msg = red(record.msg)
            return super(CliFormatter, self).format(record)
        record.msg = replace_last(str(record.msg).replace('\n', '\n│ '), '│', '└')
        record.msg = ' '.join((self._prefix(record), record.msg))
        return super(CliFormatter, self).format(record)

    def formatException(self, ei):
        '''Indent traceback info for better readability'''
        out = super(CliFormatter, self).formatException(ei)
        out = '\n'.join('│ {0}'.format(line) for line in out.splitlines())
        return replace_last(out, '│', '└')

    def _prefix(self, record):
        if record.levelno == logging.INFO:
            return cyan(ARROW)
        elif record.levelno == DRYRUN:
            return magenta(DEBUG)
        else:
            color = LEVEL_COLORS.get(record.levelno, white)
            return '{0}:'.format(color(record.levelname.upper()))


class CliHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            err = record.levelno >= logging.WARNING
            click.echo(msg, err=err)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def dryrun(self, message, *args, **kwargs):
    if self.isEnabledFor(DRYRUN):
        self._log(DRYRUN, message, args, **kwargs)


def diff(self, message, *args, **kwargs):
    if self.isEnabledFor(DIFF):
        self._log(DIFF, message, args, **kwargs)


def declare():
    '''
    Declare new log levels.

    Monkypatching is required instead of proper sublcassing
    to fix logger declared before init.
    '''
    logging.addLevelName(DRYRUN, 'DRYRUN')
    logging.addLevelName(DIFF, 'DIFF')
    logging.Logger.dryrun = dryrun
    logging.Logger.diff = diff


def init_logging(verbose=False):
    declare()
    logger = logging.getLogger()
    handler = CliHandler()
    handler.setFormatter(CliFormatter())
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


if __name__ == '__main__':  # pragma: no cover
    init_logging(verbose=True)

    logger = logging.getLogger(__name__)
    logger.debug('debug')
    logger.dryrun('dryrun')
    logger.diff('diff')
    logger.diff('+ diff')
    logger.diff('- diff')
    logger.info('info')
    logger.info('info\nmulti\nlines')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
    try:
        raise Exception('An exception')
    except Exception:
        logger.exception('exception')
