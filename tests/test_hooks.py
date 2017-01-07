# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from datetime import datetime
from mock import patch, MagicMock, ANY
from textwrap import dedent

from bumpr.config import ObjectDict
from bumpr.helpers import BumprError
from bumpr.hooks import ReadTheDocHook, CommandsHook, ChangelogHook
from bumpr.version import Version

import pytest


class ReadTheDocHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.releaser = MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'id': 'fake',
            'url': 'http://{id}.somewhere.io/{tag}',
            'bump': '{version}',
            'prepare': 'latest',
        })
        self.hook = ReadTheDocHook(self.releaser)

    def test_bump(self):
        replacements = []
        self.hook.bump(replacements)
        assert replacements == [('http://fake.somewhere.io/latest', 'http://fake.somewhere.io/1.2.3')]

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        assert replacements == [('http://fake.somewhere.io/1.2.3', 'http://fake.somewhere.io/latest')]


@patch('bumpr.hooks.execute')
class CommandsHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.releaser = MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'bump': 'bump command',
            'prepare': 'prepare command',
        })
        self.releaser.config.verbose = False
        self.releaser.config.dryrun = False
        self.hook = CommandsHook(self.releaser)

    def test_bump(self, execute):
        self.hook.bump([])
        execute.assert_called_once_with('bump command', replacements=ANY, verbose=ANY, dryrun=False)

    def test_prepare(self, execute):
        self.hook.prepare([])
        execute.assert_called_once_with('prepare command', replacements=ANY, verbose=ANY, dryrun=False)

    def test_bump_dryrun(self, execute):
        self.hook.dryrun = True
        self.hook.bump([])
        execute.assert_called_once_with('bump command', replacements=ANY, verbose=ANY, dryrun=True)

    def test_prepare_dryrun(self, execute):
        self.hook.dryrun = True
        self.hook.prepare([])
        execute.assert_called_once_with('prepare command', replacements=ANY, verbose=ANY, dryrun=True)


class ChangelogHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.releaser = MagicMock()
        self.releaser.prev_version = Version.parse('1.2.3.dev')
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.next_version = Version.parse('1.2.4.dev')
        self.releaser.timestamp = datetime.now()
        self.releaser.config.__getitem__.return_value = ObjectDict({})
        self.releaser.config.encoding = 'utf8'
        self.releaser.config.verbose = False
        self.releaser.config.dryrun = False

    def test_validate_no_file(self):
        with pytest.raises(BumprError):
            ChangelogHook(self.releaser)

    def test_validate_file_does_not_exists(self, workspace):
        self.releaser.config.__getitem__.return_value = ObjectDict({'file': 'changelog'})
        with pytest.raises(BumprError):
            ChangelogHook(self.releaser)

    def test_validate(self, workspace):
        workspace.write('changelog', '')
        self.releaser.config.__getitem__.return_value = ObjectDict({'file': 'changelog'})
        ChangelogHook(self.releaser)

    def test_bump(self, workspace):
        content = dedent('''\
            Dev
            ###

            - some changes
        ''')
        workspace.write('changelog', content)

        self.releaser.config.__getitem__.return_value = ObjectDict({
            'file': 'changelog',
            'separator': '#',
            'bump': '{version} {date:%Y-%m-%d}',
            'prepare': 'Dev',
            'empty': 'Empty',
        })

        hook = ChangelogHook(self.releaser)
        hook.bump([])

        expected = dedent('''\
            1.2.3 {0:%Y-%m-%d}
            ################

            - some changes
        ''').format(self.releaser.timestamp)

        self.releaser.perform.assert_called_once_with('changelog', content, expected)

    def test_prepare(self, workspace):
        content = dedent('''\
            1.2.3 {0:%Y-%m-%d}
            ################

            - some changes
        ''').format(self.releaser.timestamp)

        workspace.write('changelog', content)

        self.releaser.config.__getitem__.return_value = ObjectDict({
            'file': 'changelog',
            'separator': '#',
            'bump': '{version} {date:%Y-%m-%d}',
            'prepare': 'Dev',
            'empty': 'Empty',
        })

        hook = ChangelogHook(self.releaser)
        hook.prepare([])

        expected = dedent('''\
            Dev
            ###

            - Empty

            1.2.3 {0:%Y-%m-%d}
            ################

            - some changes
        ''').format(self.releaser.timestamp)

        self.releaser.perform.assert_called_once_with('changelog', content, expected)
