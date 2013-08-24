Hooks
=====

Read the doc
------------

This hook allow to change the Read The Doc documentation URL in both bump and prepare phase.

- **key**: ``readthedoc``
- **parameters**
    - id: ``None``
    - url: ``http://{id}.readthedocs.org/en/{tag}``
    - bump: ``{version}``
    - prepare: ``latest``


Most of the the time, you will just have to specify your readthedoc project identifier.

.. code-block:: ini

    [readthedoc]
    id = myproject


You can customize the generated (and parsed) URL and the string to bump in.

.. code-block:: ini

    [readthedoc]
    url = http://custom.doc/{tag}

You can also customize the tag part in the url for the bump and prepare phase

.. code-block:: ini

    [readthedoc]
    bump = {version}
    prepare = lastest


Changelog
---------

This hook allow to bump and prepare your changelog.
In the bump phase it will bump the current developpement header with a versionned one.
In the prepare phase, it will do the inverse operation.

- **key**: ``changelog``
- **parameters**
    - file: ``None``
    - separator: ``-``
    - bump: ``{version} ({date:%Y-%m-%d})'``
    - prepare: ``Current``
    - empty: ``Nothing yet``

The file parameter is mandatory and designate the changelog file.

The separator parameter spcify the character user to underline your changelog section.

.. code-block:: rst

    Changelog
    =========

    In development
    ~~~~~~~~~~~~~~

    - Another feature

    Version 1.0.1 (2013-08-23)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Some new feature

To handle this changelog you will have the following configuration

.. code-block:: ini

    [changelog]
    file = CHANGELOG
    separator = ~
    bump = Version {version} ({date:%Y-%m-%d})
    prepare = In development
    empty = Empty

If you execute Bump'R, the changelog will be bumped like:

.. code-block:: rst

    Changelog
    =========

    Version 1.0.2 (2013-08-24)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Another feature

    Version 1.0.1 (2013-08-23)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Some new feature

And then prepared:

.. code-block:: rst

    Changelog
    =========

    In development
    ~~~~~~~~~~~~~~

    - Empty

    Version 1.0.2 (2013-08-24)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Another feature

    Version 1.0.1 (2013-08-23)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Some new feature

Commands
--------

This hook allow to execute custom commands during bump and prepare phases.

- **key**: ``commands``
- **parameters**
    - bump: ``{version}``
    - prepare: ``latest``

Both bump and prepare command can be mutiline (a command statement by line),
and support the following format token:

- **version**: the current phase version string
- **major**: the current phase version major part
- **minor**: the current phase version minor part
- **patch**: the current phase version patch part
- **date**: the current date (aka. the release date)

In the bump phase, version will be the bumped version
whereas in the prepare phase it will be the prepared/next version.

_Exemple:_

.. code-block:: ini

    [commands]
    bump = echo "{major}.{minor} - {date:%Y-%m-%d)"
    prepare = echo "Next version: {version}"
