Workflow
========

When you execute Bump'R it will follow the following workflow:

#. clean
#. test
#. bump
#. publish
#. prepare

If you have been using Maven, it's inspired by the Maven Release Plugin.


Clean phase
-----------

Optionnal phase that simply execute the commands provided by the ``clean``
configuration parameter.


Test phase
----------

Optionnal phase that simply execute the commands provided by the ``tests``
configuration parameter.


Bump phase
----------

This is the main phase in which Bump'R will:

#. Compute replacements
#. Execute the bump phase for each hook
#. Bump replacement in version file and extra files
#. Commit the changes if a VCS is configured with ``commit=True``
#. Tag the previously created commit if ``tag=True``


Publish phase
-------------

Optionnal phase that simply execute the commands provided by the ``publish``
configuration parameter.

Most of the time for Python project, you will want to execute:

    ``python setup.py sdist register upload``


Prepare phase
-------------

This is the second main phase in which Bump'R will:

#. Compute replacements
#. Execute the prepare phase for each hook
#. Bump replacement in version file and extra files
#. Commit the changes if a VCS is configured with ``commit=True``
