#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys

from setuptools import setup, find_packages


PYPI_RST_FILTERS = (
    # Replace code-blocks
    (r'\.\.\s? code-block::\s*(\w|\+)+',  '::'),
    # Remove travis ci badge
    (r'.*travis-ci\.org/.*', ''),
    # Remove pypip.in badges
    (r'.*pypip\.in/.*', ''),
    (r'.*crate\.io/.*', ''),
    (r'.*coveralls\.io/.*', ''),
)


def rst(filename):
    '''
    Load rst file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - travis ci build badge
    '''
    content = open(filename).read()
    for regex, replacement in PYPI_RST_FILTERS:
        content = re.sub(regex, replacement, content)
    return content


long_description = '\n'.join((
    rst('README.rst'),
    rst('CHANGELOG.rst'),
    ''
))


install_requires = []
tests_require = ['mock', 'nose', 'rednose']
doc_require = ['sphinx']
qa_require = ['flake8', 'coverage']

if sys.version_info[0:2] < (2, 7):
    install_requires.append('argparse')
    tests_require.append('unittest2==0.5.1')


setup(
    name='bumpr',
    version=__import__('bumpr.__about__').__version__,
    description=__import__('bumpr.__about__').__description__,
    long_description=long_description,
    url='https://github.com/noirbizarre/bumpr',
    download_url='http://pypi.python.org/pypi/bumpr',
    author='Axel Haustant',
    author_email='noirbizarre+github@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    license='LGPL',
    use_2to3=True,
    entry_points={
        'console_scripts': [
            'bumpr = bumpr:main',
        ],
        'nose.plugins.0.10': [
            'dryrun-logger = bumpr.tests:DryRunLoggerPlugin'
        ],
    },
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'doc': doc_require,
        'qa': qa_require,
    },
    keywords='version bump release tag',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
)
