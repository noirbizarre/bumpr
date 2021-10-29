# Configuration file

The `bumpr.rc` configuration file is an inifile with the following possible sections and keys.

!!! note
    You can also use the `setup.cfg` file to store the configuration.
    It's recommanded to prefix section with `bumpr:` (_ie._`[bumpr:bump]`).
    Be carefull, when using Python 3, `setup.cfg` is parsed with ConfigParser and perform string interpolation.

## Sections

### bumpr

This is the main section defining the common behavior and parameters.

`file` (_default:_ `None`)
: The file containing the version string to extract.

`regex` (_default:_ `r'(__version__|VERSION)\s*=\s*(\'|")(?P<version>.+?)(\'|")'`)
: The regex used to extract the version string. It must have a
  version` named group.

`encoding` (_default:_ `utf8`)
: The files encoding.

`vcs`: (_default:_ `None`)
: Version configuration tool used (one of `git`, `mercurial` or `bazaar`)

`commit` (_default:_ `True`)
: If `True` and vcs is defined, commit the changes.

`push` (_default:_ `False`)
: If `True` and vcs is defined, push the changes and the tags to the upstream repository.

`tag` (_default:_ `True`)
: If `True` and vcs is defined, tag the version.

`tag_format` (_default:_ `{version}`)
: Specify the format of the tag

`tag_annotation` (_default:_ `None`)
: Specify an optional tag annotation formatted with the `{version}` token

`verbose` (_default:_ `False`)
: If `True`, display verbose output and command line output.

`dryrun` (_default:_ `False`)
: If `True`, no command or VCS operation will be executed. They will be displayed in the command output.

`clean` (_default:_ `None`)
: Specify the commands to be executed on the *clean* phase. Should have a single command by line.

`tests` (_default:_ `None`)
: Specify the commands to be executed on the *test* phase. Should have a single command by line.

`publish` (_default:_ `None`)
: Specify the commands to be executed on the *publish* phase. Should have a single command by line.

`files` (_default:_ `[]`)
: Extra files to process. Those files will be processed by hooks to. Specify one file by line.

### bump

This section define the bump phase behavior.

`unsuffix` (_default:_ `True`)
: If `True` the current verion suffix will be removed.

`suffix` (_default:_ `None`)
: If set, this suffix will ba appended to the version.

`part` (_default:_ `None`)
: Specify the part to bump between `major`, `minor` or `patch`.

`message` (_default:_ `Bump version {version}`)
: Specify the commit message that will be bumped.
  You can use the following token in your format pattern:
  `version`, `major`, `minor`, `patch` and `date`.
  All formating operations are accepted.

### prepare

This section define the prepare phase behavior.

`unsuffix` (_default:_ `False`)
: If `True` the current verion suffix will be removed.

`suffix` (_default:_ `None`)
: If set, this suffix will ba appended to the version.

`part` (_default:_ `patch`)
: Specify the part to bump between `major`, `minor` or `patch`.

`message` (_default:_ `Bump version {version}`)
: Specify the commit message that will be bumped.
  You can use the following token in your format pattern:
  `version`, `major`, `minor`, `patch` and `date`.
  All formating operations are accepted.

## hooks

Each hook can contribute to configuration with its own section.

See [hooks](./hooks.md).

## sample

Here a sample `bumpr.rc` file

```ini
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
```
