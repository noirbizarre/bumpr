# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch, MagicMock, ANY

from bumpr.config import ObjectDict
from bumpr.hooks import ReadTheDocHook, CommandHook
from bumpr.version import Version


class ReadTheDocHookTest(unittest.TestCase):
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
        self.assertEqual(replacements, [('http://fake.somewhere.io/latest', 'http://fake.somewhere.io/1.2.3')])

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        self.assertEqual(replacements, [('http://fake.somewhere.io/1.2.3', 'http://fake.somewhere.io/latest')])


@patch('bumpr.hooks.execute')
class CommandHookTest(unittest.TestCase):
    def setUp(self):
        self.releaser = MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'bump': 'bump command',
            'prepare': 'prepare command',
        })
        self.releaser.config.verbose = False
        self.releaser.config.dryrun = False
        self.hook = CommandHook(self.releaser)

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
