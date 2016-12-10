# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals, absolute_import

import sys

from invoke import run as rawrun, task

from os.path import join, abspath, dirname

ROOT = abspath(join(dirname(__file__)))


def color(code):
    '''A simple ANSI color wrapper factory'''
    return lambda t: '\033[{0}{1}\033[0;m'.format(code, t)


green = color('1;32m')
red = color('1;31m')
cyan = color('1;36m')

OK = '✔'
KO = '✘'
WARNING = '⚠'


def info(text):
    '''Display informations'''
    print(cyan('>>> {0}'.format(text)))
    sys.stdout.flush()


def error(text):
    print(red(' '.join((KO, text))))
    sys.stdout.flush()


def exit(text):
    error(text)
    sys.exit(-1)


def run(command, **kwargs):
    return rawrun('cd {0} && {1}'.format(ROOT, command), **kwargs)


@task
def clean(ctx, docs=False, bytecode=False, extra=''):
    '''Cleanup all build artifacts'''
    info(clean.__doc__)
    patterns = [
        'build', 'dist', 'cover', 'htmlcov', 'docs/_build', '**/*.pyc',
        '*.egg-info', '.tox', '**/__pycache__', '.cache',
    ]
    for pattern in patterns:
        print('Removing {0}'.format(pattern))
        run('rm -rf {0}'.format(pattern))


@task
def test(ctx):
    '''Run tests suite'''
    info(test.__doc__)
    run('pytest', pty=True)


@task
def cover(ctx):
    '''Run tests suite with coverage'''
    info(cover.__doc__)
    run('pytest --cov-report html --cov-report term --cov bumpr', pty=True)


@task
def tox(ctx):
    '''Run test in all Python versions'''
    info(tox.__doc__)
    run('tox', pty=True)


@task
def qa(ctx):
    '''Run a quality report'''
    info('Python static analysis')
    flake8_results = run('flake8 bumpr --jobs 1', pty=True, warn=True)
    if flake8_results.failed:
        exit(flake8_results.return_code)
    print(green('OK'))


@task
def doc(ctx):
    '''Build the documentation'''
    info(doc.__doc__)
    run('cd doc && make html', pty=True)


@task
def completion(ctx):
    '''Generate bash completion script'''
    info(completion.__doc__)
    run('_bumpr_COMPLETE=source bumpr > bumpr-complete.sh', pty=True)


@task
def dist(ctx):
    '''Package for distribution'''
    run('python setup.py sdist bdist_wheel', pty=True)


@task(clean, tox, doc, qa, dist, default=True)
def all(ctx):
    pass
