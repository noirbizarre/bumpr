#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Pymp: Python release bumper

- Prompt for versions
- Clean-up release artifact
- Bump version and tag it
- Build a source distrbution and upload on PyPI
- Update version for new develpoment cycle
'''
from __future__ import print_function, unicode_literals

import argparse
import logging

from os.path import exists

try:
    from ConfigParser import RawConfigParser  # pylint: disable=F0401
except ImportError:
    from configparser import RawConfigParser  # pylint: disable=F0401

from bumpr.hooks import HOOKS
from bumpr.version import Version, PARTS

logger = logging.getLogger(__name__)

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
        'part': 'patch',
        'message': 'Update to version {version} for next development cycle',
    },
}


class ObjectDict(dict):
    '''A dictionnary with object-like attribute access and depp merge'''
    def __init__(self, *args, **kwargs):  # pylint: disable=W0231
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ObjectDict):
            value = ObjectDict(value)
        self[key] = value

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, ObjectDict):
            value = ObjectDict(value)
        super(ObjectDict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            if isinstance(value, dict) and not isinstance(value, ObjectDict):
                value = ObjectDict(value)
            self[key] = value

    def merge(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            if isinstance(value, dict):
                if not isinstance(value, ObjectDict):
                    value = ObjectDict(value)
                if key in self and isinstance(self[key], ObjectDict):
                    self[key].merge(value)
                    continue
            self[key] = value


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
                self[hook.key] = hook.defaults
                self[hook.key].update(config.items(hook.key))
            else:
                self[hook.key] = False

    def override_from_args(self, parsed_args):
        for arg in 'file', 'vcs', 'verbose', 'dryrun', 'files':
            if arg in parsed_args and getattr(parsed_args, arg) not in (None, [], tuple()):
                self[arg] = getattr(parsed_args, arg)

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

    @classmethod
    def parse_args(cls, args=None):
        from bumpr import __version__, __description__
        parser = argparse.ArgumentParser(description=__description__)
        parser.add_argument('file', help='Versionned module file', nargs='?')
        parser.add_argument('files', help='Files to update', nargs='*')

        parser.add_argument('--version', action='version', version=__version__)

        # Bump behavior for release
        parser.add_argument('-M', '--major', dest='part', action='store_const',
                            const=Version.MAJOR, help="Bump major version")
        parser.add_argument('-m', '--minor', dest='part', action='store_const',
                            const=Version.MINOR, help="Bump minor version")
        parser.add_argument('-p', '--patch', dest='part', action='store_const',
                            const=Version.PATCH, help="Bump patch version")
        parser.add_argument('-s', '--suffix', dest='suffix', type=str, help="Set suffix")
        parser.add_argument('-u', '--unsuffix', dest='unsuffix', action='store_true', default=None, help="Unset suffix")

        # Bump behavior for prepare version
        parser.add_argument('-pM', '--prepare-major', dest='prepare_part', action='store_const',
                            const=Version.MAJOR, help="Bump major version")
        parser.add_argument('-pm', '--prepare-minor', dest='prepare_part', action='store_const',
                            const=Version.MINOR, help="Bump minor version")
        parser.add_argument('-pp', '--prepare-patch', dest='prepare_part', action='store_const',
                            const=Version.PATCH, help="Bump patch version")
        parser.add_argument('-ps', '--prepare-suffix', dest='prepare_suffix', type=str, help="Set suffix")
        parser.add_argument('-pu', '--prepare-unsuffix', dest='prepare_unsuffix', action='store_true',
            help="Unset suffix")

        parser.add_argument('--vcs', choices=['git', 'hg'], default=None, help='VCS implementation')

        parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Verbose output")
        parser.add_argument('-c', '--config', default='bumpr.rc', help='Specify a configuration file')
        parser.add_argument('-d', '--dryrun', action='store_true', help='Do not write anything and display a diff')

        parsed_args = parser.parse_args(args)
        return cls(parsed_args=parsed_args)
