# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import sys

from os.path import exists

try:
    from ConfigParser import RawConfigParser
except ImportError:
    from configparser import RawConfigParser

from bumpr.helpers import ObjectDict
from bumpr.hooks import HOOKS
from bumpr.version import PARTS

logger = logging.getLogger(__name__)
IS_PY3 = sys.version_info[0] == 3

DEFAULTS = {
    'file': None,
    'regex': r'(__version__|VERSION)\s*=\s*(\'|")(?P<version>.+?)(\'|")',
    'encoding': 'utf8',
    'vcs': None,
    'commit': True,
    'tag': True,
    'tag_format': '{version}',
    'tag_annotation': None,
    'push': False,
    'verbose': False,
    'dryrun': False,
    'clean': None,
    'tests': None,
    'skip_tests': False,
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
        'part': None,
        'message': 'Update to version {version} for next development cycle',
    },
}


class ValidationError(ValueError):
    pass


class BumprConfigParser(RawConfigParser):
    '''
    A config parser with optionnal implicit `bumpr:` prefix on sections.

    Allow better isolation in setup.cfg.
    '''
    prefix = 'bumpr'

    def candidate_sections(self, section):
        return [section, '{0}:{1}'.format(self.prefix, section)]

    def has_section(self, section):
        sections = self.candidate_sections(section)
        return any(RawConfigParser.has_section(self, section) for section in sections)

    def options(self, section):
        for section in self.candidate_sections(section):
            if RawConfigParser.has_section(self, section):
                return RawConfigParser.options(self, section)

    def has_option(self, section, option):
        sections = self.candidate_sections(section)
        return any(RawConfigParser.has_option(self, section, option) for section in sections)

    def get(self, section, option, **kwargs):
        for section in self.candidate_sections(section):
            if RawConfigParser.has_option(self, section, option):
                return RawConfigParser.get(self, section, option)

    def getboolean(self, section, option):
        for section in self.candidate_sections(section):
            if RawConfigParser.has_option(self, section, option):
                return RawConfigParser.getboolean(self, section, option)

    def items(self, section):
        for section in self.candidate_sections(section):
            if RawConfigParser.has_section(self, section):
                return RawConfigParser.items(self, section)


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

        if exists('setup.cfg'):
            self.override_from_config('setup.cfg')

        if parsed_args:
            if 'config' in parsed_args and exists(parsed_args['config']):
                self.override_from_config(parsed_args['config'])
            self.override_from_args(parsed_args)

    def override_from_config(self, filename):
        config = BumprConfigParser()
        if IS_PY3:
            config.read_file(open(filename))
        else:
            config.readfp(open(filename))

        # Common options
        if config.has_section('bumpr'):
            for option in config.options('bumpr'):
                if option in ('tag', 'commit', 'push', 'skip_tests'):
                    self[option] = config.getboolean('bumpr', option)
                elif option == 'files':
                    self.files = [name.strip() for name in config.get('bumpr', 'files').split('\n') if name.strip()]
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
        for arg in 'file', 'vcs', 'files':
            if arg in parsed_args and parsed_args.get(arg) not in (None, [], tuple()):
                self[arg] = parsed_args[arg]

        for arg in 'verbose', 'dryrun':
            if arg in parsed_args and parsed_args[arg]:
                self[arg] = True

        if parsed_args.get('commit') is not None:
            self.commit = parsed_args['commit']
        for attr in 'push', 'skip_tests':
            if parsed_args.get(attr) is not None:
                self[attr] = parsed_args[attr]

        # Bump
        if parsed_args.get('part') is not None:
            self.bump.part = parsed_args['part']
        if parsed_args.get('suffix') is not None:
            self.bump.suffix = parsed_args['suffix']
        if parsed_args.get('unsuffix') is not None:
            self.bump.unsuffix = parsed_args['unsuffix']

    def validate(self):
        if not self.file:
            raise ValidationError('A file is required from the configuration file or the command line')
