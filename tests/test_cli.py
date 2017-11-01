# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from textwrap import dedent

from bumpr.version import Version

import pytest
import yaml


@pytest.fixture
def parsed_args(workspace, mocker, options):
    config = mocker.patch('bumpr.config.Config.__init__')

    workspace.bumpr(options)
    yield config.call_args[1]['parsed_args']


def test_help(workspace):
    assert workspace.bumpr('--help').exit_code == 0
    assert workspace.bumpr('-h').exit_code == 0
    assert workspace.bumpr('-?').exit_code == 0


def test_version(workspace):
    import bumpr
    result = workspace.bumpr('--version')
    assert result.exit_code == 0
    assert result.output == bumpr.__version__ + '\n'


@pytest.mark.parametrize('options', [''])
def test_default(parsed_args):
    assert parsed_args['verbose'] is False
    assert parsed_args['dryrun'] is False
    assert parsed_args['config'] == 'bumpr.rc'
    assert parsed_args['skip_tests'] is False
    assert parsed_args['vcs'] is None
    assert parsed_args['commit'] is None
    assert parsed_args['push'] is None
    assert parsed_args['part'] is None
    assert parsed_args['suffix'] is None
    assert parsed_args['unsuffix'] is None


@pytest.mark.parametrize('options', ['-v', '--verbose'])
def test_verbose(parsed_args):
    assert parsed_args['verbose'] is True


@pytest.mark.parametrize('options', ['-d', '--dryrun'])
def test_dryrun(parsed_args):
    assert parsed_args['dryrun'] is True


@pytest.mark.parametrize('options', ['-c another'])
def test_config(parsed_args):
    assert parsed_args['config'] == 'another'


@pytest.mark.parametrize('options', ['-st', '--skip-tests'])
def test_skip_tests(parsed_args):
    assert parsed_args['skip_tests'] is True


@pytest.mark.parametrize('options', ['-s rc1', '--suffix rc1'])
def test_suffix(parsed_args):
    assert parsed_args['suffix'] == 'rc1'


@pytest.mark.parametrize('options', ['-u', '--unsuffix'])
def test_unsuffix(parsed_args):
    assert parsed_args['unsuffix'] is True


@pytest.mark.parametrize('options,expected', [
    ('--vcs git', 'git'),
    ('--vcs bzr', 'bzr'),
    ('--vcs hg', 'hg'),
])
def test_vcs(parsed_args, expected):
    assert parsed_args['vcs'] == expected


@pytest.mark.parametrize('options,expected', [
    ('--major', Version.MAJOR),
    ('--minor', Version.MINOR),
    ('--patch', Version.PATCH),
    ('-M', Version.MAJOR),
    ('-m', Version.MINOR),
    ('-p', Version.PATCH),
])
def test_part(parsed_args, expected):
    assert parsed_args['part'] == expected


@pytest.mark.parametrize('options,expected', [
    ('-C', True), ('--commit', True),
    ('-nc', False), ('--no-commit', False),
])
def test_commit(parsed_args, expected):
    assert parsed_args['commit'] == expected


@pytest.mark.parametrize('options,expected', [
    ('-P', True), ('--push', True),
    ('-np', False), ('--no-push', False),
])
def test_push(parsed_args, expected):
    assert parsed_args['push'] == expected


def test_invalid_config(workspace):
    workspace.write('bumpr.rc', 'wrong-format')
    result = workspace.bumpr()
    assert result.exit_code == 1
    assert result.output.startswith('Invalid configuration:')


def test_full_run(workspace):
    workspace.write('bumpr.rc', dedent('''\
        [bumpr]
        file=fake.py

        [prepare]
        part = patch
        suffix = dev
    '''))
    assert workspace.bumpr().exit_code == 0
    assert "__version__ = '1.2.4.dev'" in workspace.module.open().read()


def test_init_with_parameters(workspace):
    params = 'init -s bumpr/__init__.py -c CHANGELOG.rst'
    assert workspace.bumpr(params).exit_code == 0
    assert (workspace.root / 'bumpr.yml').exists()

    data = yaml.load(workspace.read('bumpr.yml'))

    assert data['source'] == 'bumpr/__init__.py'
    assert data['changelog']['file'] == 'CHANGELOG.rst'
