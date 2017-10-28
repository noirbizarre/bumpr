#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os

from setuptools import setup, find_packages


def rst(filename):
    '''
    Load rst file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - travis ci build badge
    '''
    return io.open(filename).read()


def pip(name):
    '''Parse requirements file'''
    with io.open(os.path.join('requirements', '{0}.pip'.format(name))) as f:
        return f.readlines()


long_description = '\n'.join((
    rst('README.rst'),
    rst('CHANGELOG.rst'),
    ''
))


install_requires = pip('install')
tests_require = pip('test')

setup(
    name='bumpr',
    version=__import__('bumpr.__about__').__version__,
    description=__import__('bumpr.__about__').__description__,
    long_description=long_description,
    url='https://github.com/noirbizarre/bumpr',
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
    },
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'doc': pip('doc'),
    },
    keywords='version bump release tag',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
)
