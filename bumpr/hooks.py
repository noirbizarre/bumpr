# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import codecs
import logging

from os.path import exists

from bumpr.helpers import execute, BumprError

logger = logging.getLogger(__name__)

__all_ = (
    'Hook',
    'ReadTheDocHook',
    'ChangelogHook',
    'CommandHook',
    'HOOKS',
)


class Hook(object):
    key = None
    defaults = None

    def __init__(self, releaser):
        self.releaser = releaser
        self.verbose = releaser.config.verbose
        self.dryrun = releaser.config.dryrun
        self.config = releaser.config[self.key]
        self.validate()

    def validate(self):
        '''Override this method to implement initial validation'''

    def bump(self, replacements):
        pass

    def prepare(self, replacements):
        pass


class ReadTheDocHook(Hook):
    '''
    This hook set the readthedoc url corresponding to the version
    '''
    key = 'readthedoc'
    defaults = {
        'id': None,
        'url': 'http://{id}.readthedocs.org/en/{tag}',
        'bump': '{version}',
        'prepare': 'latest',
    }

    def url(self, tag):
        return self.config.url.format(id=self.config.id, tag=tag)

    def bump(self, replacements):
        replacements.insert(0, (
            self.url('latest'),
            self.url(self.releaser.version)
        ))

    def prepare(self, replacements):
        replacements.insert(0, (
            self.url(self.releaser.version),
            self.url('latest')
        ))


class ChangelogHook(Hook):
    '''
    This hook bump the changelog version header and prepare a new section for the next release.
    '''
    key = 'changelog'
    defaults = {
        'file': None,
        'separator': '-',
        'bump': '{version} ({date:%Y-%m-%d})',
        'prepare': 'Current',
        'empty': 'Nothing yet',
    }

    def validate(self):
        if not self.config.get('file'):
            raise BumprError('Changelog file has not been specified')
        elif not exists(self.config.file):
            raise BumprError('Changelog file does not exists')

    def bump(self, replacements):
        with codecs.open(self.config.file, 'r', self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.dev_header(), self.bumped_header())
        self.releaser.perform(self.config.file, before, after)

    def prepare(self, replacements):
        next_header = '\n'.join((self.dev_header(), '', '- {0}'.format(self.config.empty), '', self.bumped_header()))
        with codecs.open(self.config.file, 'r', self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.bumped_header(), next_header)
        self.releaser.perform(self.config.file, before, after)

    def dev_header(self):
        return self.underline(self.config.prepare)

    def bumped_header(self):
        title = self.config.bump.format(
            version=self.releaser.version,
            date=self.releaser.timestamp,
            **self.releaser.version.__dict__
        )
        return self.underline(title)

    def underline(self, text):
        return '\n'.join((text, len(text) * self.config.separator))


class CommandsHook(Hook):
    '''
    This hook execute commands
    '''
    key = 'commands'
    defaults = {
        'bump': None,
        'prepare': None,
    }

    def bump(self, replacements):
        if self.config.bump:
            replacements = dict(
                version=self.releaser.version,
                date=self.releaser.timestamp,
                **self.releaser.version.__dict__
            )
            execute(self.config.bump, replacements=replacements, verbose=self.verbose, dryrun=self.dryrun)

    def prepare(self, replacements):
        if self.config.prepare:
            replacements = dict(
                version=self.releaser.next_version,
                date=self.releaser.timestamp,
                **self.releaser.next_version.__dict__
            )
            execute(self.config.prepare, replacements=replacements, verbose=self.verbose, dryrun=self.dryrun)

HOOKS = (ReadTheDocHook, ChangelogHook, CommandsHook)
