# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import logging

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
        self.config = releaser.config[self.key]

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

    def bump(self, replacements):
        self.dev_header = self.underline(self.config.prepare)  # pylint: disable=W0201
        title = self.config.bump.format(
            version=self.releaser.version,
            date=self.releaser.timestamp,
            **self.releaser.version.__dict__
        )
        self.bumped_header = self.underline(title)  # pylint: disable=W0201

        with codecs.open(self.config.file, 'r', self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.dev_header, self.bumped_header)
        self.releaser.perform(self.config.file, before, after)

    def prepare(self, replacements):
        next_header = '\n'.join((self.dev_header, '', '- {}'.format(self.config.empty), '', self.bumped_header))
        with codecs.open(self.config.file, 'r', self.releaser.config.encoding) as changelog_file:
            before = changelog_file.read()
            after = before.replace(self.bumped_header, next_header)
        self.releaser.perform(self.config.file, before, after)

    def underline(self, text):
        return '\n'.join((text, len(text) * self.config.separator))


class CommandHook(Hook):
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
            self.releaser.execute(self.config.bump)

    def prepare(self, replacements):
        if self.config.prepare:
            self.releaser.execute(self.config.prepare)

HOOKS = (ReadTheDocHook, ChangelogHook, CommandHook)
