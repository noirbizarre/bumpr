# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import io
import sys

import pytest

from copy import deepcopy
from textwrap import dedent

from bumpr.config import DEFAULTS, Config, ValidationError, __name__ as config_module_name
from bumpr.version import Version
from bumpr.hooks import HOOKS, ReadTheDocHook

if sys.version_info[0] == 3:
    unicode = str


@pytest.fixture
def mock_ini(mocker):
    def inner(data):
        open_name = '{0}.open'.format(config_module_name)
        return mocker.patch(open_name, return_value=io.StringIO(unicode(dedent(data))), create=True)
    return inner


@pytest.fixture
def bumprc(request, mocker, mock_ini):
    marker = request.node.get_marker('bumprc')
    if marker:
        data = marker.args[0]
        mocker.patch('bumpr.config.exists', return_value=True)
        yield mock_ini(data)
    else:
        yield


@pytest.mark.usefixtures('bumprc')
class ConfigTest(object):

    @pytest.fixture(autouse=True)
    def cleandir(self, tmpdir):
        tmpdir.chdir()
        yield

    def test_defaults(self):
        '''It should initialize with default values'''
        config = Config()
        expected = deepcopy(DEFAULTS)
        for hook in HOOKS:
            expected[hook.key] = False
        assert config == expected

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
        assert config == expected

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
        assert config == expected

    def test_override_from_config(self, mock_ini):
        bumprrc = '''\
        [bumpr]
        file = test.py
        files = README
        push = true
        [bump]
        message = test
        '''

        expected = deepcopy(DEFAULTS)
        expected['file'] = 'test.py'
        expected['files'] = ['README']
        expected['push'] = True
        expected['bump']['message'] = 'test'
        for hook in HOOKS:
            expected[hook.key] = False

        config = Config()
        mock = mock_ini(bumprrc)
        config.override_from_config('test.rc')

        mock.assert_called_once_with('test.rc')
        assert config == expected

    def test_override_from_setup_cfg(self):
        with io.open('setup.cfg', 'w') as cfg:
            cfg.write('\n'.join([
                '[bumpr]',
                'file = test.py',
                'files = README',
                'push = true',
                '[bumpr:bump]',
                'message = test',
            ]))

        expected = deepcopy(DEFAULTS)
        expected['file'] = 'test.py'
        expected['files'] = ['README']
        expected['push'] = True
        expected['bump']['message'] = 'test'
        for hook in HOOKS:
            expected[hook.key] = False

        config = Config()
        assert config == expected

    def test_override_from_setup_cfg_with_hooks(self):
        tested_hook = ReadTheDocHook
        with io.open('setup.cfg', 'w') as cfg:
            cfg.write('\n'.join([
                '[bumpr:{0}]'.format(tested_hook.key),
                'bump = test',
            ]))

        expected = deepcopy(DEFAULTS)
        for hook in HOOKS:
            if hook is tested_hook:
                expected[hook.key] = hook.defaults
                expected[hook.key]['bump'] = 'test'
            else:
                expected[hook.key] = False

        config = Config()
        assert config == expected

    def test_override_hook_from_config(self, mock_ini):
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
        mock = mock_ini(bumprrc)
        config.override_from_config('test.rc')

        mock.assert_called_once_with('test.rc')
        assert config == expected

    def test_override_from_args(self):
        config = Config(parsed_args={'verbose': True, 'part': Version.MAJOR, 'suffix': 'rc1', 'unsuffix': True})

        expected = deepcopy(DEFAULTS)
        expected['verbose'] = True
        expected['bump']['part'] = Version.MAJOR
        expected['bump']['suffix'] = 'rc1'
        expected['bump']['unsuffix'] = True
        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        files = README
        [bump]
        message = test
        [prepare]
        part = minor
    ''')
    def test_override_args_keeps_config_values(self):
        config = Config(parsed_args={'part': Version.MAJOR, 'verbose': True})

        expected = deepcopy(DEFAULTS)
        expected['files'] = ['README']
        expected['bump']['part'] = Version.MAJOR
        expected['bump']['message'] = 'test'
        expected['verbose'] = True

        expected['prepare']['part'] = Version.MINOR

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        push = true
    ''')
    def test_do_not_override_push_when_not_in_args(self, mocker, mock_ini):
        config = Config(parsed_args={'push': None})

        expected = deepcopy(DEFAULTS)
        expected['push'] = True

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        push = true
    ''')
    def test_override_push_from_args(self):
        config = Config(parsed_args={'push': False})

        expected = deepcopy(DEFAULTS)
        expected['push'] = False

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        push = false
    ''')
    def test_force_push_from_args(self):
        config = Config(parsed_args={'push': True})

        expected = deepcopy(DEFAULTS)
        expected['push'] = True

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        commit = False
    ''')
    def test_do_not_override_commit_when_not_in_args(self):
        config = Config(parsed_args={'commit': None})

        expected = deepcopy(DEFAULTS)
        expected['commit'] = False

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        commit = true
    ''')
    def test_override_no_commit(self):
        config = Config(parsed_args={'commit': False})

        expected = deepcopy(DEFAULTS)
        expected['commit'] = False

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('''\
        [bumpr]
        commit = false
    ''')
    def test_override_commit(self):
        config = Config(parsed_args={'commit': True})

        expected = deepcopy(DEFAULTS)
        expected['commit'] = True

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    @pytest.mark.bumprc('[bumpr]')
    def test_skip_tests_from_args(self):
        config = Config(parsed_args={'skip_tests': True})

        expected = deepcopy(DEFAULTS)
        expected['skip_tests'] = True

        for hook in HOOKS:
            expected[hook.key] = False

        assert config == expected

    def test_validate(self):
        config = Config({'file': 'version.py'})
        config.validate()

    def test_validate_file_missing(self):
        config = Config()
        with pytest.raises(ValidationError):
            config.validate()
