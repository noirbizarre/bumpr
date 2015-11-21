# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import io
import sys

try:
    import unittest2 as unittest
except:
    import unittest

from contextlib import contextmanager
from copy import deepcopy
from mock import patch
from textwrap import dedent

from bumpr.config import DEFAULTS, Config, ValidationError, __name__ as config_module_name
from bumpr.version import Version
from bumpr.hooks import HOOKS, ReadTheDocHook

if sys.version_info[0] == 3:
    unicode = str  # pylint: disable=W0622,C0103


@contextmanager
def mock_ini(data):
    open_name = '{0}.open'.format(config_module_name)
    with patch(open_name, return_value=io.StringIO(unicode(dedent(data))), create=True) as mock:
        yield mock


class ConfigTest(unittest.TestCase):
    maxDiff = None

    def test_defaults(self):
        '''It should initialize with default values'''
        config = Config()
        expected = deepcopy(DEFAULTS)
        for hook in HOOKS:
            expected[hook.key] = False
        self.assertDictEqual(config, expected)

    def test_from_dict(self):
        '''It can take a dictionnay as parameter but keeps defaults'''
        config_dict = {
            'module': 'test_module',
            'attribute': 'VERSION',
            'commit': True,
            'tag': True,
            'dryrun': True,
            'files': ['anyfile.py'],
            'bump': {
                'suffix': 'final',
                'message': 'Version {version}',
            },
            'prepare': {
                'part': 'minor',
                'suffix': 'dev',
                'message': 'Update to version {version}',
            },
        }
        config = Config(config_dict)
        expected = deepcopy(DEFAULTS)
        for key, value in config_dict.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    expected[key][nested_key] = nested_value
            else:
                expected[key] = value
        for hook in HOOKS:
            expected[hook.key] = False
        self.assertDictEqual(config, expected)

    def test_from_dict_with_hook(self):
        '''It should take defaults from hooks if present and set it to false if not'''
        tested_hook = ReadTheDocHook
        config_dict = {
            tested_hook.key: {
                'bump': 'test'
            }
        }

        expected = deepcopy(DEFAULTS)
        for hook in HOOKS:
            if hook is tested_hook:
                expected[hook.key] = hook.defaults
                expected[hook.key]['bump'] = 'test'
            else:
                expected[hook.key] = False

        config = Config(config_dict)
        self.assertDictEqual(config, expected)

    def test_override_from_config(self):
        bumprrc = '''\
        [bumpr]
        file = test.py
        files = README
        [bump]
        message = test
        '''

        expected = deepcopy(DEFAULTS)
        expected['file'] = 'test.py'
        expected['files'] = ['README']
        expected['bump']['message'] = 'test'
        for hook in HOOKS:
            expected[hook.key] = False

        config = Config()
        with mock_ini(bumprrc) as mock:
            config.override_from_config('test.rc')

        mock.assert_called_once_with('test.rc')
        self.assertDictEqual(config, expected)

    def test_override_hook_from_config(self):
        tested_hook = ReadTheDocHook
        bumprrc = '''\
        [{0}]
        bump = test
        '''.format(tested_hook.key)

        expected = deepcopy(DEFAULTS)
        for hook in HOOKS:
            if hook is tested_hook:
                expected[hook.key] = hook.defaults
                expected[hook.key]['bump'] = 'test'
            else:
                expected[hook.key] = False

        config = Config()
        with mock_ini(bumprrc) as mock:
            config.override_from_config('test.rc')

        mock.assert_called_once_with('test.rc')
        self.assertDictEqual(config, expected)

    def test_override_from_args(self):
        config = Config.parse_args(['test.py', '-M', '-v', '-s', 'test-suffix', '-c', 'fake'])

        expected = deepcopy(DEFAULTS)
        expected['file'] = 'test.py'
        expected['bump']['part'] = Version.MAJOR
        expected['bump']['suffix'] = 'test-suffix'
        expected['verbose'] = True
        for hook in HOOKS:
            expected[hook.key] = False

        self.assertDictEqual(config, expected)

    def test_override_args_keeps_config_values(self):
        bumprrc = '''\
        [bumpr]
        files = README
        [bump]
        message = test
        [prepare]
        part = minor
        '''

        with mock_ini(bumprrc):
            with patch('bumpr.config.exists', return_value=True):
                config = Config.parse_args(['test.py', '-M', '-v', '-s', 'test-suffix', '-c', 'test.rc'])

        expected = deepcopy(DEFAULTS)
        expected['file'] = 'test.py'
        expected['bump']['part'] = Version.MAJOR
        expected['bump']['suffix'] = 'test-suffix'
        expected['verbose'] = True

        expected['files'] = ['README']
        expected['bump']['message'] = 'test'
        expected['prepare']['part'] = Version.MINOR

        for hook in HOOKS:
            expected[hook.key] = False

        self.assertDictEqual(config, expected)

    def test_validate(self):
        config = Config({'file': 'version.py'})
        config.validate()

    def test_validate_file_missing(self):
        config = Config()
        with self.assertRaises(ValidationError):
            config.validate()
