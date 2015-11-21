# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
import logging
import sys

from os.path import exists

try:
    from ConfigParser import RawConfigParser  # pylint: disable=F0401
except ImportError:
    from configparser import RawConfigParser  # pylint: disable=F0401

from bumpr.helpers import ObjectDict
from bumpr.hooks import HOOKS
from bumpr.version import Version, PARTS

logger = logging.getLogger(__name__)
IS_PY3 = sys.version_info[0] == 3

DEFAULTS = {
    'file': None,
    'regex': r'(__version__|VERSION)\s*=\s*(\'|")(?P<version>.+?)(\'|")',
    'encoding': 'utf8',
    'vcs': None,
    'commit': True,
    'tag': True,
    'verbose': False,
    'dryrun': False,
    'clean': None,
    'tests': None,
    'publish': None,
    'bump_only': False,
    'prepare_only': False,
    'files': [],

    'bump': {
        'unsuffix': True,
        'suffix': None,
        'part': None,
        'message': 'Bump version {version}',
    },

    'prepare': {
        'unsuffix': False,
        'suffix': None,
        'part': None,
        'message': 'Update to version {version} for next development cycle',
    },
}


class ValidationError(ValueError):
    pass


class Config(ObjectDict):
    def __init__(self, source=None, parsed_args=None):
        super(Config, self).__init__(DEFAULTS)
        for hook in HOOKS:
            self[hook.key] = False

        if source:
            for hook in HOOKS:
                if hook.key in source:
                    self.merge({hook.key: hook.defaults})
            self.merge(source)

        if parsed_args:
            if 'config' in parsed_args and exists(parsed_args.config):
                self.override_from_config(parsed_args.config)
            self.override_from_args(parsed_args)

    def override_from_config(self, filename):
        config = RawConfigParser()
        if IS_PY3:
            config.read_file(open(filename))
        else:
            config.readfp(open(filename))

        # Common options
        if config.has_section('bumpr'):
            for option in config.options('bumpr'):
                if option in ('tag', 'commit'):
                    self[option] = config.getboolean('bumpr', option)
                elif option == 'files':
                    # pylint: disable=W0201
                    self.files = [name.strip() for name in config.get('bumpr', 'files').split('\n') if name.strip()]
                    # pylint: enable=W0201
                else:
                    self[option] = config.get('bumpr', option)

        # Bump and next section
        for section in 'bump', 'prepare':
            for option in 'message', 'suffix':
                if config.has_option(section, option):
                    self[section][option] = config.get(section, option)
            if config.has_option(section, 'unsuffix'):
                self[section]['unsuffix'] = config.getboolean(section, 'unsuffix')

            if config.has_option(section, 'part'):
                self[section]['part'] = PARTS[config.get(section, 'part').lower()]

        for hook in HOOKS:
            if config.has_section(hook.key):
                if not self.get(hook.key, False):
                    self[hook.key] = hook.defaults
                self[hook.key].update(config.items(hook.key))
            else:
                self[hook.key] = False

    def override_from_args(self, parsed_args):
        for arg in 'file', 'vcs', 'verbose', 'dryrun', 'files':
            if arg in parsed_args and getattr(parsed_args, arg) not in (None, [], tuple()):
                self[arg] = getattr(parsed_args, arg)

        self.commit = not parsed_args.nocommit  # pylint: disable=W0201
        self.bump_only = parsed_args.bump_only  # pylint: disable=W0201
        self.prepare_only = parsed_args.prepare_only  # pylint: disable=W0201

        # Bump
        if parsed_args.part is not None:
            self.bump.part = parsed_args.part
        if parsed_args.suffix is not None:
            self.bump.suffix = parsed_args.suffix
        if parsed_args.unsuffix is not None:
            self.bump.unsuffix = parsed_args.unsuffix

        # Next
        if parsed_args.prepare_part is not None:
            self.prepare.part = parsed_args.prepare_part
        if parsed_args.prepare_suffix is not None:
            self.prepare.suffix = parsed_args.prepare_suffix
        if parsed_args.prepare_unsuffix is not None:
            self.prepare.unsuffix = parsed_args.prepare_unsuffix

    def validate(self):
        if not self.file:
            raise ValidationError('A file is required from the configuration file or the command line')

    @classmethod
    def parse_args(cls, args=None):
        from bumpr import __version__, __description__
        parser = argparse.ArgumentParser(description=__description__)

        parser.add_argument('file', help='Versionned module file', nargs='?')
        parser.add_argument('files', help='Files to update', nargs='*')

        parser.add_argument('--version', action='version', version=__version__)
        parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Verbose output")
        parser.add_argument('-c', '--config', default='bumpr.rc', help='Specify a configuration file')
        parser.add_argument('-d', '--dryrun', action='store_true', help='Do not write anything and display a diff')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-b', '--bump', dest='bump_only', action='store_true', help='Only perform the bump')
        group.add_argument('-pr', '--prepare', dest='prepare_only', action='store_true',
            help='Only perform the prepare')

        # Bump behavior for bump
        group = parser.add_argument_group('bump')
        group.add_argument('-M', '--major', dest='part', action='store_const', const=Version.MAJOR,
                help="Bump major version")
        group.add_argument('-m', '--minor', dest='part', action='store_const', const=Version.MINOR,
                help="Bump minor version")
        group.add_argument('-p', '--patch', dest='part', action='store_const',
                const=Version.PATCH, help="Bump patch version")
        group.add_argument('-s', '--suffix', dest='suffix', type=str, help="Set suffix")
        group.add_argument('-u', '--unsuffix', dest='unsuffix', action='store_true', default=None, help="Unset suffix")

        # Bump behavior for prepare version
        group = parser.add_argument_group('prepare')
        group.add_argument('-pM', '--prepare-major', dest='prepare_part', action='store_const',
                const=Version.MAJOR, help="Bump major version")
        group.add_argument('-pm', '--prepare-minor', dest='prepare_part', action='store_const',
                const=Version.MINOR, help="Bump minor version")
        group.add_argument('-pp', '--prepare-patch', dest='prepare_part', action='store_const',
                const=Version.PATCH, help="Bump patch version")
        group.add_argument('-ps', '--prepare-suffix', dest='prepare_suffix', type=str, help="Set suffix")
        group.add_argument('-pu', '--prepare-unsuffix', dest='prepare_unsuffix', action='store_true',
                help="Unset suffix")

        group = parser.add_argument_group('Version control system')
        group.add_argument('--vcs', choices=['git', 'hg'], default=None, help='VCS implementation')
        group.add_argument('-nc', '--nocommit', action='store_true', help='Do not commit')

        parsed_args = parser.parse_args(args)
        return cls(parsed_args=parsed_args)
