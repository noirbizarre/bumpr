# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals, absolute_import

import sys
import os

from invoke import task

ROOT = os.path.dirname(__file__)

CLEAN_PATTERNS = [
    '**/*.pyc',
    '**/__pycache__',
    '*.egg-info',
    '.cache',
    '.tox',
    'build',
    'dist',
    'docs/_build',
    'reports',
]


def color(code):
    '''A simple ANSI color wrapper factory'''
    return lambda t: '\033[{0}{1}\033[0;m'.format(code, t)


green = color('1;32m')
red = color('1;31m')
blue = color('1;30m')
cyan = color('1;36m')
purple = color('1;35m')
white = color('1;39m')


def header(text):
    '''Display an header'''
    print(' '.join((blue('>>'), cyan(text))))
    sys.stdout.flush()


def info(text, *args, **kwargs):
    '''Display informations'''
    text = text.format(*args, **kwargs)
    print(' '.join((purple('>>>'), text)))
    sys.stdout.flush()


def success(text):
    '''Display a success message'''
    print(' '.join((green('✔'), white(text))))
    sys.stdout.flush()


def error(text):
    '''Display an error message'''
    print(red('✘ {0}'.format(text)))
    sys.stdout.flush()


def exit(text=None, code=-1):
    if text:
        error(text)
    sys.exit(code)


@task
def clean(ctx):
    '''Cleanup all build artifacts'''
    header(clean.__doc__)
    with ctx.cd(ROOT):
        for pattern in CLEAN_PATTERNS:
            info(pattern)
            ctx.run('rm -rf {0}'.format(' '.join(CLEAN_PATTERNS)))


@task
def deps(ctx):
    '''Install or update development dependencies'''
    header(deps.__doc__)
    with ctx.cd(ROOT):
        ctx.run('pip install -r requirements/develop.pip -r requirements/doc.pip', pty=True)


@task
def test(ctx, report=False, verbose=False):
    '''Run tests suite'''
    header(test.__doc__)
    cmd = ['pytest']
    if verbose:
        cmd.append('-v')
    if report:
        cmd.append('--junitxml=reports/python/tests.xml')
    with ctx.cd(ROOT):
        ctx.run(' '.join(cmd), pty=True)


@task
def cover(ctx, report=False, verbose=False):
    '''Run tests suite with coverage'''
    header(cover.__doc__)
    cmd = [
        'pytest',
        '--cov-config coverage.rc',
        '--cov-report term',
        '--cov-report html:reports/coverage',
        '--cov-report xml:reports/coverage.xml',
        '--cov=bumpr',
    ]
    if verbose:
        cmd.append('-v')
    if report:
        cmd += [
            '--cov-report html:reports/python/coverage',
            '--cov-report xml:reports/python/coverage.xml',
            '--junitxml=reports/python/tests.xml'
        ]
    with ctx.cd(ROOT):
        ctx.run(' '.join(cmd), pty=True)


@task
def qa(ctx):
    '''Run a quality report'''
    header(qa.__doc__)
    with ctx.cd(ROOT):
        info('Python Static Analysis')
        flake8_results = ctx.run('flake8 bumpr', pty=True, warn=True)
        if flake8_results.failed:
            error('There is some lints to fix')
        else:
            success('No lint to fix')
        info('Ensure PyPI can render README and CHANGELOG')
        readme_results = ctx.run('python setup.py check -r -s', pty=True, warn=True, hide=True)
        if readme_results.failed:
            print(readme_results.stdout)
            error('README and/or CHANGELOG is not renderable by PyPI')
        else:
            success('README and CHANGELOG are renderable by PyPI')
    if flake8_results.failed or readme_results.failed:
        exit('Quality check failed', flake8_results.return_code or readme_results.return_code)
    success('Quality check OK')


@task
def tox(ctx):
    '''Run test in all Python versions'''
    header(tox.__doc__)
    ctx.run('tox', pty=True)


@task
def doc(ctx):
    '''Build the documentation'''
    header(doc.__doc__)
    with ctx.cd(os.path.join(ROOT, 'doc')):
        ctx.run('make html', pty=True)
    success('Documentation available in doc/_build/html')


@task
def completion(ctx):
    '''Generate bash completion script'''
    header(completion.__doc__)
    with ctx.cd(ROOT):
        ctx.run('_bumpr_COMPLETE=source bumpr > bumpr-complete.sh', pty=True)
    success('Completion generated in bumpr-complete.sh')


@task
def dist(ctx):
    '''Package for distribution'''
    header(dist.__doc__)
    with ctx.cd(ROOT):
        ctx.run('python setup.py bdist_wheel', pty=True)
    success('Distribution is available in dist directory')


@task(clean, deps, test, qa, doc, dist, default=True)
def all(ctx):
    '''Run all tasks (default)'''
    pass
