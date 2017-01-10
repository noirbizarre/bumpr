# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import pytest

from mock import patch, MagicMock, ANY

from bumpr.config import Config
from bumpr.helpers import BumprError
from bumpr.releaser import Releaser
from bumpr.version import Version


def workspace_version(version):
    def wrapper(wrapped):
        wrapped.__version = version
        return wrapped
    return wrapper


class ReleaserTest(object):
    def test_constructor(self, workspace):
        config = Config({
            'file': 'fake.py'
        })
        releaser = Releaser(config)

        assert isinstance(releaser.prev_version, Version)
        assert str(releaser.prev_version) == '1.2.3.dev'

        assert isinstance(releaser.version, Version)
        assert isinstance(releaser.next_version, Version)

        assert releaser.timestamp is None

        assert not hasattr(releaser, 'vcs')
        assert not hasattr(releaser, 'diffs')

        assert releaser.hooks == []

    def test_constructor_version_not_found(self, workspace):
        config = Config({
            'file': 'fake.py'
        })
        workspace.write('fake.py', '')
        with pytest.raises(BumprError):
            Releaser(config)

    def test_constructor_version_bad_format(self, workspace):
        config = Config({
            'file': 'fake.py',
        })
        workspace.write('fake.py', '__badversion__ = "1.2.3"')
        with pytest.raises(BumprError):
            Releaser(config)

    def test_constructor_with_hooks(self, workspace):
        config = Config({
            'file': 'fake.py'
        })
        hooks = []
        for i in range(3):
            key = 'hook{0}'.format(i)
            config[key] = True
            mock = MagicMock()
            mock.key = key
            hooks.append(mock)

        with patch('bumpr.releaser.HOOKS', hooks) as mock:
            releaser = Releaser(config)
            for hook in hooks:
                hook.assert_called_with(releaser)

    def test_test(self, workspace):
        config = Config({
            'file': 'fake.py',
            'tests': 'test command',
        })
        releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.test()
            execute.assert_called_with('test command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_skip_test(self, workspace):
        config = Config({
            'file': 'fake.py',
            'tests': 'test command',
            'skip_tests': True,
        })
        releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.test()
            assert not execute.called

    def test_publish(self, workspace):
        config = Config({
            'file': 'fake.py',
            'publish': 'publish command',
        })

        releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.publish()
            execute.assert_called_with('publish command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_clean(self, workspace):
        config = Config({
            'file': 'fake.py',
            'clean': 'clean command',
        })
        releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.clean()
            execute.assert_called_with('clean command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_commit(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake'})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.commit('message')
            vcs.commit.assert_called_with('message')

    def test_commit_no_commit(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'commit': False})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.commit('message')
            assert not vcs.commit.called

    def test_tag(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake'})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.tag()
            vcs.tag.assert_called_with(str(releaser.version))

    def test_tag_no_commit(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'commit': False})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.tag()
            assert not vcs.tag.called

    def test_tag_no_tag(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'tag': False})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.tag()
            assert not vcs.tag.called

    def test_tag_custom_pattern(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'tag_pattern': 'v{version}'})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.tag()
            vcs.tag.assert_called_with('v{0}'.format(releaser.version))

    def test_push_disabled_by_default(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake'})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.push()
            assert not vcs.push.called

    def test_push(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'push': True})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.push()
            assert vcs.push.called

    def test_push_no_commit(self, workspace):
        config = Config({'file': 'fake.py', 'vcs': 'fake', 'push': True, 'commit': False})
        releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.push()
            assert not vcs.push.called

    def test_release_wihtout_vcs_or_commands(self, workspace):
        config = Config({'file': 'fake.py', 'files': [workspace.readme_filename]})
        releaser = Releaser(config)
        with patch('bumpr.releaser.execute') as execute:
            with patch.object(releaser, 'commit') as commit:
                releaser.release()
                assert not execute.called
                assert not commit.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.3' in content
                assert '1.2.3.dev' not in content

    def test_bump(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
        })

        releaser = Releaser(config)
        hook = MagicMock()
        with patch.object(releaser, 'hooks', [hook]):
            with patch.object(releaser, 'commit') as commit:
                with patch.object(releaser, 'tag') as tag:
                    releaser.bump()
                    assert not commit.called
                    assert not tag.called
                    assert hook.bump.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.3' in content
                assert '1.2.3.dev' not in content

    def test_bump_vcs(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
        })
        releaser = Releaser(config)
        with patch.object(releaser, 'commit') as commit:
            with patch.object(releaser, 'tag') as tag:
                releaser.bump()
                assert commit.call_count == 1
                assert tag.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.3' in content
                assert '1.2.3.dev' not in content

    def test_release(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
            'push': True,
        })
        releaser = Releaser(config)
        with patch.object(releaser, 'clean') as clean:
            with patch.object(releaser, 'test') as test:
                with patch.object(releaser, 'bump') as bump:
                    with patch.object(releaser, 'publish') as publish:
                        with patch.object(releaser, 'prepare') as prepare:
                            with patch.object(releaser, 'push') as push:
                                releaser.release()
                                assert clean.called
                                assert test.called
                                assert bump.called
                                assert publish.called
                                assert prepare.called
                                assert push.called

    def test_release_bump_only(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
            'push': True,
            'bump_only': True
        })
        releaser = Releaser(config)
        with patch.object(releaser, 'clean') as clean:
            with patch.object(releaser, 'test') as test:
                with patch.object(releaser, 'bump') as bump:
                    with patch.object(releaser, 'publish') as publish:
                        with patch.object(releaser, 'prepare') as prepare:
                            with patch.object(releaser, 'push') as push:
                                releaser.release()
                                assert not clean.called
                                assert not test.called
                                assert bump.called
                                assert not publish.called
                                assert not prepare.called
                                assert not push.called

    def test_release_prepare_only(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
            'push': True,
            'prepare_only': True
        })
        releaser = Releaser(config)
        with patch.object(releaser, 'clean') as clean:
            with patch.object(releaser, 'test') as test:
                with patch.object(releaser, 'bump') as bump:
                    with patch.object(releaser, 'publish') as publish:
                        with patch.object(releaser, 'prepare') as prepare:
                            with patch.object(releaser, 'push') as push:
                                releaser.release()
                                assert not clean.called
                                assert not test.called
                                assert not bump.called
                                assert not publish.called
                                assert prepare.called
                                assert not push.called

    def test_release_dryrun(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
            'dryrun': True,
            'push': True,
        })
        releaser = Releaser(config)
        with patch('bumpr.releaser.execute') as execute:
            with patch.object(releaser, 'vcs') as vcs:
                releaser.release()
                assert not execute.called
                assert not vcs.commit.called
                assert not vcs.tag.called
                assert not vcs.push.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.3.dev' in content
                assert '1.2.4' not in content

    @workspace_version('1.2.3')
    def test_prepare(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'prepare': {
                'part': Version.PATCH,
                'suffix': 'dev',
            }
        })
        releaser = Releaser(config)
        hook = MagicMock()
        with patch.object(releaser, 'hooks', [hook]):
            with patch.object(releaser, 'commit') as commit:
                with patch.object(releaser, 'tag') as tag:
                    releaser.prepare()
                    assert not commit.called
                    assert not tag.called
                    assert hook.prepare.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.4.dev' in content
                assert '1.2.3' not in content

    @workspace_version('1.2.3')
    def test_prepare_vcs(self, workspace):
        config = Config({
            'file': 'fake.py',
            'files': [workspace.readme_filename],
            'vcs': 'fake',
            'prepare': {
                'part': Version.PATCH,
                'suffix': 'dev',
            }
        })

        releaser = Releaser(config)
        with patch.object(releaser, 'commit') as commit:
            with patch.object(releaser, 'tag') as tag:
                releaser.prepare()
                assert commit.call_count, 1
                assert not tag.called

        for filename in workspace.module_filename, workspace.readme_filename:
            with open(filename) as f:
                content = f.read()
                assert '1.2.4.dev' in content
                assert '1.2.3' not in content
