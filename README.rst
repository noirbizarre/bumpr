======
Bump'R
======

.. image:: https://secure.travis-ci.org/noirbizarre/bumpr.svg?branch=master
    :target: https://travis-ci.org/noirbizarre/bumpr
    :alt: Build status
.. image:: https://codecov.io/gh/noirbizarre/bumpr/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/noirbizarre/bumpr/branch/master
    :alt: Code coverage
.. image:: https://readthedocs.org/projects/bumpr/badge/?version=latest
    :target: https://bumpr.readthedocs.io/en/latest/
    :alt: Documentation status
.. image:: https://img.shields.io/pypi/v/bumpr.svg
    :target: https://pypi.python.org/pypi/bumpr
    :alt: Last version
.. image:: https://img.shields.io/pypi/l/bumpr.svg
    :target: https://pypi.python.org/pypi/bumpr
    :alt: License
.. image:: https://img.shields.io/pypi/pyversions/bumpr.svg
    :target: https://pypi.python.org/pypi/bumpr
    :alt: Supported Python versions

Bump'R is a version bumper and releaser allowing in a single command:

- Clean-up release artifact
- Bump version and tag it
- Build a source distribution and upload on PyPI
- Update version for a new development cycle

Bump'R intend to be customizable with the following features:

- Optionnal test suite run before bump
- Customizable with a config file
- Overridable by command line
- Extensible with hooks


Compatibility
=============

Bump'R requires Python 2.7 or 3.4+


Installation
============

You can install Bump'R with pip:

.. code-block:: console

    $ pip install bumpr


Usage
=====

You can use directly the command line to setup every parameter:

.. code-block:: console

    $ bumpr fake/__init__.py README.rst -M -ps dev

But Bump'R is designed to work with a configuration file (``bumpr.rc`` by defaults).
Some features are only availables with the configuration file like:

- commit message customization
- hooks configuration
- multiline test, clean and publish commands

Here's an exemple:

.. code-block:: ini

    [bumpr]
    file = fake/__init__.py
    vcs = git
    tests = tox
    publish = python setup.py sdist register upload
    clean =
        python setup.py clean
        rm -rf *egg-info build dist
    files = README.rst

    [bump]
    unsuffix = true
    message = Bump version {version}

    [prepare]
    suffix = dev
    message = Prepare version {version} for next development cycle

    [changelog]
    file = CHANGELOG.rst
    bump = {version} ({date:%Y-%m-%d})
    prepare = In development

    [readthedoc]
    id = fake

This way you only have to specify which part you want to bump on the command line:

.. code-block:: console

    $ bumpr -M  # Bump the major
    $ bumpr     # Bump the default part aka. patch


Documentation
=============

The documentation is hosted `on Read the Docs <https://bumpr.readthedocs.io/en/latest/>`_
