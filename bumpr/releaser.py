# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import logging
import re

from datetime import datetime
from difflib import unified_diff

from bumpr.helpers import execute
from bumpr.hooks import HOOKS
from bumpr.vcs import VCS
from bumpr.version import Version

logger = logging.getLogger(__name__)


class Releaser(object):
    '''
    Release workflow executor
    '''
    def __init__(self, config):
        self.config = config

        with open(config.file) as f:
            match = re.search(config.regex, f.read())
            try:
                version_string = match.group('version')
                self.prev_version = Version.parse(version_string)
            except:
                raise ValueError('Version not found in {}'.format(config.file))

        self.version = self.prev_version.copy()
        self.version.bump(config.bump.part, config.bump.unsuffix, config.bump.suffix)

        self.next_version = self.version.copy()
        self.next_version.bump(config.prepare.part, config.prepare.unsuffix, config.prepare.suffix)

        self.timestamp = None

        if config.vcs:
            self.vcs = VCS[config.vcs](verbose=config.verbose)

        if config.dryrun:
            self.diffs = {}

        self.hooks = [hook(self) for hook in HOOKS if self.config[hook.key]]

    def execute(self, command, version=None):
        version = version or self.version
        replacements = dict(version=version, date=self.timestamp, **version.__dict__)
        execute(command, replacements=replacements, dryrun=self.config.dryrun, verbose=self.config.verbose)

    def release(self):
        logger.info('Performing release')
        self.timestamp = datetime.now()

        if self.config.bump_only:
            self.bump()
        elif self.config.prepare_only:
            self.prepare()
        else:
            self.clean()
            self.test()
            self.bump()
            self.publish()
            self.prepare()

    def test(self):
        if self.config.tests:
            logger.info('Running test suite')
            self.execute(self.config.tests)

    def bump(self):
        logger.info('Bump version %s', self.version)

        replacements = [
            (str(self.prev_version), str(self.version))
        ]

        for hook in self.hooks:
            hook.bump(replacements)

        self.bump_version_file(self.prev_version, self.version)
        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(self.config.bump.message.format(
                version=self.version,
                date=self.timestamp,
                **self.version.__dict__
            ))
            self.tag()

        if self.config.dryrun:
            self.display_diff()
            self.diffs.clear()

    def prepare(self):
        logger.info('Prepare version %s', self.next_version)

        replacements = [
            (str(self.version), str(self.next_version))
        ]

        for hook in self.hooks:
            hook.prepare(replacements)

        self.bump_version_file(self.version, self.next_version)
        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(self.config.prepare.message.format(
                version=self.next_version,
                date=self.timestamp,
                **self.next_version.__dict__
            ))

        if self.config.dryrun:
            self.display_diff()

    def clean(self):
        '''Clean the workspace'''
        if self.config.clean:
            logger.info('Cleaning')
            self.execute(self.config.clean)

    def perform(self, filename, before, after):
        if self.config.dryrun:
            diff = unified_diff(before.split('\n'), after.split('\n'), lineterm='')
            self.diffs[filename] = diff
        else:
            with open(filename, 'wb') as f:
                f.write(after.encode(self.config.encoding))

    def bump_version_file(self, from_version, to_version):
        with codecs.open(self.config.file, 'r', self.config.encoding) as f:
            before = f.read()
        after = before.replace(str(from_version), str(to_version))
        self.perform(self.config.file, before, after)

    def bump_files(self, replacements):
        for filename in self.config.files:
            with codecs.open(filename, 'r', self.config.encoding) as current_file:
                before = current_file.read()
            after = before
            for token, replacement in replacements:
                after = after.replace(token, replacement)
            self.perform(filename, before, after)

    def publish(self):
        '''Publish the current release to PyPI'''
        if self.config.publish:
            logger.info('Publish')
            self.execute(self.config.publish)

    def tag(self):
        if self.config.tag:
            logger.debug('Tag: %s', self.version)
            if not self.config.dryrun:
                self.vcs.tag(str(self.version))
            else:
                logger.dryrun('tag: {0}'.format(self.version))

    def commit(self, message):
        if self.config.commit:
            logger.debug('Commit: %s', message)
            if not self.config.dryrun:
                self.vcs.commit(message)
            else:
                logger.dryrun('commit: {0}'.format(message))

    def display_diff(self):
        for filename, diff in self.diffs.items():
            logger.diff(filename)
            for line in diff:
                logger.diff(line)
            logger.diff('')
