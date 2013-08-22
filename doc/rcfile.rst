Configuration file
==================

The ``bumpr.rc`` configuration file is an inifile with the following possible sections and keys.

bumpr
-----
This is the main section defining the common behavior and parameters.

file
    *Default:* ``None``

    The file containing the version string to extract.

regex
    *Default:* ``r'(__version__|VERSION)\s*=\s*(\'|")(?P<version>.+?)(\'|")'``

    The regex used to extract the version string.
    It must have a ``version`` named group.

encoding
    *Default:* ``utf8``

    The files encoding.

vcs
    *Default:* ``None``

commit
    *Default:* ``True``

    If ``True`` and vcs is defined, commit the changes.

tag:
    *Default:* ``True``

    If ``True`` and vcs is defined, tag the version.

verbose
    *Default:* ``False``

    If ``True``, display verbose output and command line output.


dryrun
    *Default:* ``False``

    TODO

clean
    *Default:* ``None``

    Specify the commands to be executed on the *clean* phase.
    Should have a single command by line.

tests
    *Default:* ``None``

    Specify the commands to be executed on the *test* phase.
    Should have a single command by line.

publish
    *Default:* ``None``

    Specify the commands to be executed on the *publish* phase.
    Should have a single command by line.

files
    *Default:* ``[]``

    Extra files to process. Those files will be processed by hooks to.
    Specify one file by line.

bump
----
This section define the bump phase behavior.

unsuffix
    *Default:* ``True``

    If ``True`` the current verion suffix will be removed.

suffix:
    *Default:* ``None``

    If set, this suffix will ba appended to the version.

part:
    *Default:* ``None``

    Specify the part to bump between ``major``, ``minor`` or ``patch``.

message
    *Default:* ``Bump version {version}``

    Specify the commit message that will be bumped.
    You can use the following token in your format pattern:
    ``version``, ``major``, ``minor``, ``patch`` and ``date``.
    All formating operations are accepted.

prepare
-------

This section define the prepare phase behavior.

unsuffix
    *Default:* ``False``

    If ``True`` the current verion suffix will be removed.

suffix:
    *Default:* ``None``

    If set, this suffix will ba appended to the version.

part:
    *Default:* ``patch``

    Specify the part to bump between ``major``, ``minor`` or ``patch``.

message
    *Default:* ``Update to version {version} for next development cycle``

    Specify the commit message that will be bumped.
    You can use the following token in your format pattern:
    ``version``, ``major``, ``minor``, ``patch`` and ``date``.
    All formating operations are accepted.

hooks
-----

Each hook can contribute to configuration with its own section.

See :doc:`hooks`.

sample
------

Here a sample ``bumpr.rc`` file

.. code-block:: ini

    [bumpr]
    file = fake/__init__.py
    vcs = git
    tests = tox
    publish = python setup.py register sdist upload
    clean =
        python setup.py clean
        rm -rf *egg-info build dist
    files = README.rst

    [bump]
    message = 'Commit version {version}'

    [prepare]
    suffix = dev
    message = Prepare version {version} for next development cycle

    [changelog]
    file = CHANGELOG.rst
    bump = {version} ({date:%Y-%m-%d})
    prepare = In development

    [readthedoc]
    id = bumpr
