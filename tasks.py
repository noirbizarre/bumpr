# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals, absolute_import

from invoke import run, task

from os.path import join, abspath, dirname

ROOT = abspath(join(dirname(__file__)))


def lrun(command, **kwargs):
    run('cd {0} && {1}'.format(ROOT, command), **kwargs)


@task
def clean(docs=False, bytecode=False, extra=''):
    '''Cleanup all build artifacts'''
    patterns = ['build', 'dist', 'cover', 'docs/_build', '**/*.pyc', '*.egg-info', '.tox', '**/__pycache__']
    for pattern in patterns:
        print('Removing {0}'.format(pattern))
        lrun('rm -rf {0}'.format(pattern))


@task
def test():
    '''Run tests suite'''
    lrun('nosetests --force-color', pty=True)


@task
def cover():
    '''Run tests suite with coverage'''
    lrun('nosetests --force-color --with-coverage --cover-html', pty=True)


@task
def tox():
    '''Run test in all Python versions'''
    lrun('tox', pty=True)


@task
def qa():
    '''Run a quality report'''
    lrun('flake8 bumpr')


@task
def doc():
    '''Build the documentation'''
    lrun('cd doc && make html', pty=True)


@task
def completion():
    '''Generate bash completion script'''
    lrun('_bumpr_COMPLETE=source bumpr > bumpr-complete.sh', pty=True)


@task
def dist():
    '''Package for distribution'''
    lrun('python setup.py sdist bdist_wheel', pty=True)


@task(tox, doc, qa, dist, default=True)
def all():
    pass
