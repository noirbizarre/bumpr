# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import pytest

from bumpr.config import Config
from bumpr.helpers import BumprError
from bumpr.releaser import Releaser
from bumpr.version import Version


def test_constructor(workspace):
    config = Config({
        'file': 'fake.py',
        'tag_format': 'v{version}',
    })
    releaser = Releaser(config)

    assert isinstance(releaser.prev_version, Version)
    assert str(releaser.prev_version) == '1.2.3.dev'

    assert isinstance(releaser.version, Version)
    assert isinstance(releaser.next_version, Version)

    assert releaser.timestamp is None

    assert not hasattr(releaser, 'vcs')
    assert not hasattr(releaser, 'diffs')
    assert not hasattr(releaser, 'modified')

    assert releaser.tag_label == 'v1.2.3'

    assert releaser.hooks == []


def test_constructor_version_not_found(workspace):
    config = Config({
        'file': 'fake.py'
    })
    workspace.write('fake.py', '')
    with pytest.raises(BumprError):
        Releaser(config)


def test_constructor_version_bad_format(workspace):
    config = Config({
        'file': 'fake.py',
    })
    workspace.write('fake.py', '__badversion__ = "1.2.3"')
    with pytest.raises(BumprError):
        Releaser(config)


def test_constructor_with_hooks(workspace, mocker):
    config = Config({
        'file': 'fake.py'
    })
    hooks = []
    for i in range(3):
        key = 'hook{0}'.format(i)
        config[key] = True
        mock = mocker.MagicMock()
        mock.key = key
        hooks.append(mock)
    mocker.patch('bumpr.releaser.HOOKS', hooks)

    releaser = Releaser(config)

    for hook in hooks:
        hook.assert_called_with(releaser)


def test_test(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'tests': 'test command',
    })
    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')

    releaser.test()

    execute.assert_called_with('test command', replacements=mocker.ANY, dryrun=mocker.ANY, verbose=mocker.ANY)


def test_skip_test(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'tests': 'test command',
        'skip_tests': True,
    })
    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')

    releaser.test()

    assert not execute.called


def test_publish(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'publish': 'publish command',
    })

    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')

    releaser.publish()

    execute.assert_called_with('publish command', replacements=mocker.ANY, dryrun=mocker.ANY, verbose=mocker.ANY)


def test_clean(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'clean': 'clean command',
    })
    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')

    releaser.clean()

    execute.assert_called_with('clean command', replacements=mocker.ANY, dryrun=mocker.ANY, verbose=mocker.ANY)


def test_commit(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake'})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.commit('message')

    vcs.commit.assert_called_with('message')


def test_commit_no_commit(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'commit': False})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.commit('message')

    assert not vcs.commit.called


def test_tag(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake'})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.tag()

    vcs.tag.assert_called_with(str(releaser.version))


def test_tag_no_commit(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'commit': False})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.tag()

    assert not vcs.tag.called


def test_tag_no_tag(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'tag': False})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.tag()

    assert not vcs.tag.called


def test_tag_custom_pattern(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'tag_format': 'v{version}'})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.tag()

    vcs.tag.assert_called_with('v{0}'.format(releaser.version))


def test_push_disabled_by_default(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake'})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.push()

    assert not vcs.push.called


def test_push(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'push': True})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.push()

    assert vcs.push.called


def test_push_no_commit(workspace, mocker):
    config = Config({'file': 'fake.py', 'vcs': 'fake', 'push': True, 'commit': False})
    releaser = Releaser(config)
    vcs = mocker.patch.object(releaser, 'vcs')

    releaser.push()

    assert not vcs.push.called


def test_release_wihtout_vcs_or_commands(workspace, mocker):
    config = Config({'file': 'fake.py', 'files': [str(workspace.readme)]})
    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')
    commit = mocker.patch.object(releaser, 'commit')

    releaser.release()

    assert not execute.called
    assert not commit.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.3' in content
            assert '1.2.3.dev' not in content


def test_bump(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
    })

    releaser = Releaser(config)
    hook = mocker.MagicMock()
    mocker.patch.object(releaser, 'hooks', [hook])
    commit = mocker.patch.object(releaser, 'commit')
    tag = mocker.patch.object(releaser, 'tag')

    releaser.bump()

    assert not commit.called
    assert not tag.called
    assert hook.bump.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.3' in content
            assert '1.2.3.dev' not in content


def test_bump_vcs(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
    })
    releaser = Releaser(config)
    commit = mocker.patch.object(releaser, 'commit')
    tag = mocker.patch.object(releaser, 'tag')

    releaser.bump()

    assert commit.call_count == 1
    assert tag.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.3' in content
            assert '1.2.3.dev' not in content


def test_bump_vcs_with_annotation(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'tag_annotation': 'version {version}'
    })
    releaser = Releaser(config)
    commit = mocker.patch.object(releaser, 'commit')
    tag = mocker.patch.object(releaser.vcs, 'tag')

    releaser.bump()

    assert commit.call_count == 1
    tag.assert_called_with(str(releaser.version), 'version {0}'.format(releaser.version))

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.3' in content
            assert '1.2.3.dev' not in content


def test_release(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'push': True,
    })
    releaser = Releaser(config)
    clean = mocker.patch.object(releaser, 'clean')
    test = mocker.patch.object(releaser, 'test')
    bump = mocker.patch.object(releaser, 'bump')
    publish = mocker.patch.object(releaser, 'publish')
    prepare = mocker.patch.object(releaser, 'prepare')
    push = mocker.patch.object(releaser, 'push')

    releaser.release()

    assert clean.called
    assert test.called
    assert bump.called
    assert publish.called
    assert prepare.called
    assert push.called


def test_release_bump_only(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'push': True,
        'bump_only': True
    })
    releaser = Releaser(config)
    clean = mocker.patch.object(releaser, 'clean')
    test = mocker.patch.object(releaser, 'test')
    bump = mocker.patch.object(releaser, 'bump')
    publish = mocker.patch.object(releaser, 'publish')
    prepare = mocker.patch.object(releaser, 'prepare')
    push = mocker.patch.object(releaser, 'push')

    releaser.release()

    assert not clean.called
    assert not test.called
    assert bump.called
    assert not publish.called
    assert not prepare.called
    assert not push.called


def test_release_prepare_only(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'push': True,
        'prepare_only': True
    })
    releaser = Releaser(config)
    clean = mocker.patch.object(releaser, 'clean')
    test = mocker.patch.object(releaser, 'test')
    bump = mocker.patch.object(releaser, 'bump')
    publish = mocker.patch.object(releaser, 'publish')
    prepare = mocker.patch.object(releaser, 'prepare')
    push = mocker.patch.object(releaser, 'push')

    releaser.release()

    assert not clean.called
    assert not test.called
    assert not bump.called
    assert not publish.called
    assert prepare.called
    assert not push.called


def test_release_dryrun(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'dryrun': True,
        'push': True,
    })
    releaser = Releaser(config)
    execute = mocker.patch('bumpr.releaser.execute')
    vcs = mocker.patch.object(releaser, 'vcs')
    releaser.release()
    assert not execute.called
    assert not vcs.commit.called
    assert not vcs.tag.called
    assert not vcs.push.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.3.dev' in content
            assert '1.2.4' not in content


@pytest.mark.version('1.2.3')
def test_prepare(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'prepare': {
            'part': Version.PATCH,
            'suffix': 'dev',
        }
    })
    releaser = Releaser(config)
    hook = mocker.MagicMock()
    mocker.patch.object(releaser, 'hooks', [hook])
    commit = mocker.patch.object(releaser, 'commit')
    tag = mocker.patch.object(releaser, 'tag')

    releaser.prepare()

    assert not commit.called
    assert not tag.called
    assert hook.prepare.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.4.dev' in content
            assert '1.2.3' not in content


@pytest.mark.version('1.2.3')
def test_prepare_vcs(workspace, mocker):
    config = Config({
        'file': 'fake.py',
        'files': [str(workspace.readme)],
        'vcs': 'fake',
        'prepare': {
            'part': Version.PATCH,
            'suffix': 'dev',
        }
    })
    releaser = Releaser(config)
    commit = mocker.patch.object(releaser, 'commit')
    tag = mocker.patch.object(releaser, 'tag')

    releaser.prepare()

    assert commit.call_count == 1
    assert not tag.called

    for file in workspace.module, workspace.readme:
        with file.open() as f:
            content = f.read()
            assert '1.2.4.dev' in content
            assert '1.2.3' not in content
