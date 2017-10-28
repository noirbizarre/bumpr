# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from datetime import datetime
from textwrap import dedent

from bumpr.config import ObjectDict, Config
from bumpr.helpers import BumprError
from bumpr.hooks import ReadTheDocHook, CommandsHook, ChangelogHook, ReplaceHook
from bumpr.version import Version

import pytest


class ReadTheDocHookDefaultTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, workspace, mocker):
        self.releaser = mocker.MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.tag_label = '1.2.3'
        self.releaser.config = Config({ReadTheDocHook.key: {'id': 'fake'}})
        self.hook = ReadTheDocHook(self.releaser)

    def test_bump(self):
        replacements = []
        self.hook.bump(replacements)
        assert replacements == [
            ('https://fake.readthedocs.io/en/latest', 'https://fake.readthedocs.io/en/1.2.3'),
            ('https://readthedocs.org/projects/fake/badge/?version=latest',
             'https://readthedocs.org/projects/fake/badge/?version=1.2.3'),
        ]

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        assert replacements == [
            ('https://fake.readthedocs.io/en/1.2.3', 'https://fake.readthedocs.io/en/latest'),
            ('https://readthedocs.org/projects/fake/badge/?version=1.2.3',
             'https://readthedocs.org/projects/fake/badge/?version=latest'),
        ]


class ReadTheDocHookCustomTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.releaser = mocker.MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.tag_label = '1.2.3'
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'id': 'fake',
            'url': 'http://{id}.somewhere.io/{tag}',
            'badge': 'http://{id}.somewhere.io/badge/{tag}',
            'bump': '{version}',
            'prepare': 'latest',
        })
        self.hook = ReadTheDocHook(self.releaser)

    def test_bump(self):
        replacements = []
        self.hook.bump(replacements)
        assert replacements == [
            ('http://fake.somewhere.io/latest', 'http://fake.somewhere.io/1.2.3'),
            ('http://fake.somewhere.io/badge/latest', 'http://fake.somewhere.io/badge/1.2.3'),
        ]

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        assert replacements == [
            ('http://fake.somewhere.io/1.2.3', 'http://fake.somewhere.io/latest'),
            ('http://fake.somewhere.io/badge/1.2.3', 'http://fake.somewhere.io/badge/latest'),
        ]


class ReadTheDocHookCustomTagTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, workspace, mocker):
        self.releaser = mocker.MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.tag_label = 'v1.2.3'
        self.releaser.config = Config({ReadTheDocHook.key: {'id': 'fake'}})
        self.hook = ReadTheDocHook(self.releaser)

    def test_bump(self):
        replacements = []
        self.hook.bump(replacements)
        assert replacements == [
            ('https://fake.readthedocs.io/en/latest', 'https://fake.readthedocs.io/en/v1.2.3'),
            ('https://readthedocs.org/projects/fake/badge/?version=latest',
             'https://readthedocs.org/projects/fake/badge/?version=v1.2.3'),
        ]

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        assert replacements == [
            ('https://fake.readthedocs.io/en/v1.2.3', 'https://fake.readthedocs.io/en/latest'),
            ('https://readthedocs.org/projects/fake/badge/?version=v1.2.3',
             'https://readthedocs.org/projects/fake/badge/?version=latest'),
        ]


class CommandsHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.releaser = mocker.MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'bump': 'bump command',
            'prepare': 'prepare command',
        })
        self.releaser.config.verbose = False
        self.releaser.config.dryrun = False
        self.hook = CommandsHook(self.releaser)

    def test_bump(self, mocker):
        execute = mocker.patch('bumpr.hooks.execute')
        self.hook.bump([])
        execute.assert_called_once_with('bump command', replacements=mocker.ANY, verbose=mocker.ANY, dryrun=False)

    def test_prepare(self, mocker):
        execute = mocker.patch('bumpr.hooks.execute')
        self.hook.prepare([])
        execute.assert_called_once_with('prepare command', replacements=mocker.ANY, verbose=mocker.ANY, dryrun=False)

    def test_bump_dryrun(self, mocker):
        execute = mocker.patch('bumpr.hooks.execute')
        self.hook.dryrun = True
        self.hook.bump([])
        execute.assert_called_once_with('bump command', replacements=mocker.ANY, verbose=mocker.ANY, dryrun=True)

    def test_prepare_dryrun(self, mocker):
        execute = mocker.patch('bumpr.hooks.execute')
        self.hook.dryrun = True
        self.hook.prepare([])
        execute.assert_called_once_with('prepare command', replacements=mocker.ANY, verbose=mocker.ANY, dryrun=True)


class ChangelogHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.releaser = mocker.MagicMock()
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

    def test_bump_no_separator(self, workspace):
        content = dedent('''\
            ## Dev

            - some changes
        ''')
        workspace.write('changelog', content)

        self.releaser.config.__getitem__.return_value = ObjectDict({
            'file': 'changelog',
            'separator': '',
            'bump': '## {version} {date:%Y-%m-%d}',
            'prepare': '## Dev',
            'empty': 'Empty',
        })

        hook = ChangelogHook(self.releaser)
        hook.bump([])

        expected = dedent('''\
            ## 1.2.3 {0:%Y-%m-%d}

            - some changes
        ''').format(self.releaser.timestamp)

        self.releaser.perform.assert_called_once_with('changelog', content, expected)

    def test_prepare_no_separator(self, workspace):
        content = dedent('''\
            ## 1.2.3 {0:%Y-%m-%d}

            - some changes
        ''').format(self.releaser.timestamp)

        workspace.write('changelog', content)

        self.releaser.config.__getitem__.return_value = ObjectDict({
            'file': 'changelog',
            'separator': '',
            'bump': '## {version} {date:%Y-%m-%d}',
            'prepare': '## Dev',
            'empty': 'Empty',
        })

        hook = ChangelogHook(self.releaser)
        hook.prepare([])

        expected = dedent('''\
            ## Dev

            - Empty

            ## 1.2.3 {0:%Y-%m-%d}

            - some changes
        ''').format(self.releaser.timestamp)

        self.releaser.perform.assert_called_once_with('changelog', content, expected)


class ReplaceHookTest(object):
    @pytest.fixture(autouse=True)
    def setUp(self, mocker):
        self.releaser = mocker.MagicMock()
        self.releaser.prev_version = Version.parse('1.2.3.dev')
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.next_version = Version.parse('1.2.4.dev')
        self.releaser.timestamp = datetime.now()
        self.releaser.tag_label = 'v1.2.3'
        self.releaser.config = Config()

    def test_bump(self):
        self.releaser.config[ReplaceHook.key] = {
            'dev': 'dev-{version}',
            'stable': 'stable-{tag}',
        }

        replacements = []
        hook = ReplaceHook(self.releaser)
        hook.bump(replacements)

        assert replacements == [('dev-1.2.3.dev', 'stable-v1.2.3')]

    def test_prepare_with_version(self):
        self.releaser.config[ReplaceHook.key] = {
            'dev': 'dev-{version}',
            'stable': 'stable-{tag}',
        }

        replacements = []
        hook = ReplaceHook(self.releaser)
        hook.prepare(replacements)

        assert replacements == [('stable-v1.2.3', 'dev-1.2.4.dev')]
