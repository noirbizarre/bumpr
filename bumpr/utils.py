# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

import click

ARROW = '➢'
DEBUG = '⇝'
OK = '✔'
KO = '✘'
WARNING = '⚠'


def color(name, **kwargs):
    return lambda t: click.style(str(t), fg=name, **kwargs)


green = color('green', bold=True)
yellow = color('yellow', bold=True)
red = color('red', bold=True)
cyan = color('cyan')
magenta = color('magenta', bold=True)
white = color('white', bold=True)
echo = click.echo


def header(msg):
    '''Display an header'''
    echo(' '.join((yellow('✯'), green(msg))))


def arrow(msg):
    echo('{0} {1}'.format(yellow(ARROW), msg))


def label_arrow(label, msg):
    arrow('{0}: {1}'.format(white(label), msg))


def success(msg):
    echo('{0} {1}'.format(green(OK), white(msg)))


def error(msg, details=None):
    echo(red('{0} {1}'.format(KO, msg)))
    if details:
        echo(details)


def exit(msg, details=None, code=-1):
    error(msg, details)
    sys.exit(code)
