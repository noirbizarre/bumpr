======
Bump'R
======

.. image:: https://secure.travis-ci.org/noirbizarre/bumpr.png
    :target: http://travis-ci.org/noirbizarre/bumpr
.. image:: https://coveralls.io/repos/noirbizarre/bumpr/badge.png?branch=master
    :target: https://coveralls.io/r/noirbizarre/bumpr
.. image:: https://pypip.in/v/bumpr/badge.png
    :target: https://crate.io/packages/bumpr
.. image:: https://pypip.in/d/bumpr/badge.png
    :target: https://crate.io/packages/bumpr

Bump'R is a version bumper and a python package releaser.
In a single command, it allows you:

- Clean-up release artifact
- Bump version and tag it
- Build a source distrbution and upload on PyPI
- Update version for a new development cycle

Bump'R intend to be customizable with the following features:

- Optionnal test suite run before bump
- Customizable with a config file
- Overridable by command line
- Extensible with hooks


Compatibility
=============

Bump'R requires Python 2.6+


Installation
============

You can install Bump'R with pip:

.. code-block:: console

    $ pip install bumpr

or with easy_install:

.. code-block:: console

    $ easy_install bumpr


Usage
=====

You can use directly the command line to setup every parameter:

.. code-block:: console

    $ bumpr fake/__init__.py README.rst -M -ps dev

But Bump'R is designed to work with a configuration file (``bumpr.rc`` by defaults).

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

The documentation is hosted `on Read the Docs <http://bumpr.readthedocs.org/en/latest/>`_
