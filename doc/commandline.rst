Command line usage
==================

.. code-block:: console

    $ bumpr -h
    usage: bumpr [-h] [--version] [-M] [-m] [-p] [-s SUFFIX] [-u] [-pM] [-pm]
                 [-pp] [-ps PREPARE_SUFFIX] [-pu] [--vcs {git,hg}] [-v]
                 [-c CONFIG] [-d]
                 [file] [files [files ...]]

    Version bumper and Python package releaser

    positional arguments:
      file                  Versionned module file
      files                 Files to update

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -M, --major           Bump major version
      -m, --minor           Bump minor version
      -p, --patch           Bump patch version
      -s SUFFIX, --suffix SUFFIX
                            Set suffix
      -u, --unsuffix        Unset suffix
      -pM, --prepare-major  Bump major version
      -pm, --prepare-minor  Bump minor version
      -pp, --prepare-patch  Bump patch version
      -ps PREPARE_SUFFIX, --prepare-suffix PREPARE_SUFFIX
                            Set suffix
      -pu, --prepare-unsuffix
                            Unset suffix
      --vcs {git,hg}        VCS implementation
      -v, --verbose         Verbose output
      -c CONFIG, --config CONFIG
                            Specify a configuration file
      -d, --dryrun          Do not write anything and display a diff
