# Command line usage

The bumpr executable can be used in two way:

- one shot usage with all parameters on command line
- regular usage with most of the parameters in a configuration file

The default configuration file name is `bumpr.rc` but you can override
it with the `-c` option.

All mandatory parameters not present in the configuration file should be
on command line.

```console
$ bumpr -h
usage: bumpr [-h] [--version] [-v] [-c CONFIG] [-d] [-st] [-b | -pr] [-M] [-m]
             [-p] [-s SUFFIX] [-u] [-pM] [-pm] [-pp] [-ps PREPARE_SUFFIX]
             [-pu] [--vcs {git,hg}] [-nc] [-P] [-nP]
             [file] [files [files ...]]

Version bumper and Python package releaser

positional arguments:
  file                  Versionned module file
  files                 Files to update

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         Verbose output
  -c CONFIG, --config CONFIG
                        Specify a configuration file
  -d, --dryrun          Do not write anything and display a diff
  -st, --skip-tests     Skip tests
  -b, --bump            Only perform the bump
  -pr, --prepare        Only perform the prepare

bump:
  -M, --major           Bump major version
  -m, --minor           Bump minor version
  -p, --patch           Bump patch version
  -s SUFFIX, --suffix SUFFIX
                        Set suffix
  -u, --unsuffix        Unset suffix

prepare:
  -pM, --prepare-major  Bump major version
  -pm, --prepare-minor  Bump minor version
  -pp, --prepare-patch  Bump patch version
  -ps PREPARE_SUFFIX, --prepare-suffix PREPARE_SUFFIX
                        Set suffix
  -pu, --prepare-unsuffix
                        Unset suffix

Version control system:
  --vcs {git,hg}        VCS implementation
  -nc, --nocommit       Do not commit
  -P, --push            Push changes to remote repository
  -nP, --no-push        Don't push changes to remote repository
```
