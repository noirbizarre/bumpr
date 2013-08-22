# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import logging
import re
import subprocess

from datetime import datetime
from difflib import unified_diff

from bumpr import compat
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
        self.modified = set()

        if config.vcs:
            self.vcs = VCS[config.vcs](verbose=config.verbose)

        if config.dryrun:
            self.diffs = {}

        self.hooks = [hook(self) for hook in HOOKS if self.config[hook.key]]

    def release(self):
        logger.info('Performing release')
        self.timestamp = datetime.now()
        self.clean()
        self.test()
        self.bump()
        if self.config.vcs and not self.config.dryrun:  # Does not make any sense without
            self.prepare()

    def execute(self, command, dryrun=False):
        if not command:
            return
        for cmd in command.split('\n'):
            if cmd.strip():
                cmd = cmd.format(version=self.version, date=self.timestamp, **self.version.__dict__).strip()
                if dryrun:
                    logger.info('dry run execute: {0}'.format(cmd))
                elif self.config.verbose:
                    subprocess.check_call(cmd.split())
                else:
                    try:
                        compat.check_output(cmd.split())
                    except subprocess.CalledProcessError as exception:
                        logger.error('Command "%s" failed with exit code %s', cmd, exception.returncode)
                        print(exception.output)

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
        self.commit_bump()
        self.publish()
        if self.config.verbose and self.config.dryrun:
            for filename, diff in self.diffs.items():
                print(filename)
                print(diff)
            self.diffs.clear()

    def prepare(self):
        logger.info('Prepare version %s', self.version)

        replacements = [
            (str(self.version), str(self.next_version))
        ]

        for hook in self.hooks:
            hook.prepare(replacements)

        self.bump_version_file(self.version, self.next_version)
        self.bump_files(replacements)
        self.commit_prepare()
        if self.config.verbose and self.config.dryrun:
            for filename, diff in self.diffs.items():
                print(filename)
                print(diff)

    def clean(self):
        '''Clean the workspace'''
        if self.config.clean:
            logger.info('Cleaning')
            self.execute(self.config.clean)

    def perform(self, filename, before, after):
        with open(filename, 'wb') as f:
            f.write(after.encode(self.config.encoding))
        self.modified.add(filename)
        if self.config.dryrun:
            diff = unified_diff(before.split('\n'), after.split('\n'))
            self.diffs[filename] = '\n'.join(diff)

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
            self.execute(self.config.publish, self.config.dryrun)

    def commit_bump(self):
        if self.config.vcs:
            if self.config.commit:
                self.commit(self.config.bump.message.format(
                    version=self.version,
                    date=self.timestamp,
                    **self.version.__dict__
                ))
            if self.config.tag:
                self.vcs.tag(str(self.version))

    def commit_prepare(self):
        if self.config.vcs:
            if self.config.commit:
                self.commit(self.config.prepare.message.format(
                    version=self.next_version,
                    date=self.timestamp,
                    **self.next_version.__dict__
                ))

    def commit(self, message):
        if self.config.commit and self.config.vcs:
            logger.info('Commit: %s', message)
            self.vcs.commit(message, self.modified)
            self.modified.clear()
