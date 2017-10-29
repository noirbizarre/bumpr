Changelog
=========

0.3.7 (2017-10-29)
------------------

- Drop support for Python 2.6 and 3.3
- Properly display dry run ``prepare`` diff
- Warn only for dirty workspace on dry run
- Optional tag annotation support

0.3.6 (2017-01-10)
------------------

- Make use of custom `tag_format` in readthedoc hook
- Expose `{tag}` in replace and command hook
- Expose `{tag}` in commit messages

0.3.5 (2017-01-10)
------------------

- Allow to specify a custom tag pattern

0.3.4 (2017-01-10)
------------------

- Added `-st/--skip-tests` option

0.3.3 (2017-01-08)
------------------

- Push action is verbose

0.3.2 (2017-01-08)
------------------

- Fix some boolean handling from commandline

0.3.1 (2017-01-08)
------------------

- Ensure push is executed
- Fix boolean parsing
- Fix error handling on version extraction

0.3.0 (2017-01-08)
------------------

- Support seprator omission in changelog (for markdown)
- Add readthedoc badge support.
- **Breaking** Use https and readthedocs.io as default
- `setup.cfg` declaration support
- Optionnal `bumpr:` prefix support
- Switch to pytest


0.2.1 (2015-11-21)
------------------

- Use nosetests instead of custom discovery
- Some fixes on Python 3 (mostly encodings)
- Improve error handling
- Validate configuration

0.2.0 (2013-08-24)
------------------

- colored diff
- Added ``--bump`` and ``--prepare`` to only perform bump or prepare
- Rely on VCS for tracking files and ensure working copy is clean
- Added option ``--nocommit``
- Ensure dry run does not write or execute anything
- Better output and error handling
- Group parameters in help
- Added optionnal hook vaidation
- Fix some Python incompatibilities (Python 2.6 and 3.X)
- More documentation

0.1.0 (2013-08-22)
------------------

- Initial release. Missing some parts but working!
