# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import pytest

from mock import patch

from bumpr.vcs import BaseVCS, Git, Mercurial, Bazaar
from bumpr.helpers import BumprError


class BaseVCSTest(object):
    def test_execute_verbose(self):
        vcs = BaseVCS(verbose=True)
        with patch('bumpr.vcs.execute') as execute:
            vcs.execute('cmd arg')
            execute.assert_called_with('cmd arg', verbose=True)

    def test_execute_quiet(self):
        vcs = BaseVCS(verbose=False)
        with patch('bumpr.vcs.execute') as execute:
            vcs.execute('cmd arg')
            execute.assert_called_with('cmd arg', verbose=False)


class GitTest(object):
    def test_validate_ok(self, workspace):
        workspace.mkdir('.git')
        git = Git()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '?? new.py'
            git.validate()
            execute.assert_called_with('git status --porcelain', verbose=False)

    def test_validate_ko_not_git(self, workspace):
        git = Git()

        with patch('bumpr.vcs.execute') as execute:
            with pytest.raises(BumprError):
                git.validate()
            assert execute.called is False

    def test_validate_ko_not_clean(self, workspace):
        workspace.mkdir('.git')
        git = Git()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
            with pytest.raises(BumprError):
                git.validate()
            execute.assert_called_with('git status --porcelain', verbose=False)

    def test_tag(self):
        git = Git()

        with patch.object(git, 'execute') as execute:
            git.tag('fake')
            execute.assert_called_with(['git', 'tag', 'fake'])

    def test_commit(self):
        git = Git()

        with patch.object(git, 'execute') as execute:
            git.commit('message')
            execute.assert_called_with(['git', 'commit', '-am', 'message'])

    def test_push(self):
        git = Git()

        with patch.object(git, 'execute') as execute:
            git.push()
            execute.assert_any_call(['git', 'push'])
            execute.assert_any_call(['git', 'push', '--tags'])


class MercurialTest(object):
    def test_validate_ok(self, workspace):
        workspace.mkdir('.hg')
        mercurial = Mercurial()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '?? new.py'
            mercurial.validate()
            execute.assert_called_with('hg status -mard', verbose=False)

    def test_validate_ko_not_mercurial(self, workspace):
        mercurial = Mercurial()

        with patch('bumpr.vcs.execute') as execute:
            with pytest.raises(BumprError):
                mercurial.validate()
            assert execute.called is False

    def test_validate_ko_not_clean(self, workspace):
        workspace.mkdir('.hg')
        mercurial = Mercurial()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
            with pytest.raises(BumprError):
                mercurial.validate()
            execute.assert_called_with('hg status -mard', verbose=False)

    def test_tag(self):
        mercurial = Mercurial()

        with patch.object(mercurial, 'execute') as execute:
            mercurial.tag('fake')
            execute.assert_called_with(['hg', 'tag', 'fake'])

    def test_commit(self):
        mercurial = Mercurial()

        with patch.object(mercurial, 'execute') as execute:
            mercurial.commit('message')
            execute.assert_called_with(['hg', 'commit', '-A', '-m', 'message'])

    def test_push(self):
        mercurial = Mercurial()

        with patch.object(mercurial, 'execute') as execute:
            mercurial.push()
            execute.assert_called_with(['hg', 'push'])


class BazaarTest(object):
    def test_validate_ok(self, workspace):
        workspace.mkdir('.bzr')
        bazaar = Bazaar()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '? new.py'
            bazaar.validate()
            execute.assert_called_with('bzr status --short', verbose=False)

    def test_validate_ko_not_bazaar(self, workspace):
        bazaar = Bazaar()

        with patch('bumpr.vcs.execute') as execute:
            with pytest.raises(BumprError):
                bazaar.validate()
            assert execute.called is False

    def test_validate_ko_not_clean(self, workspace):
        workspace.mkdir('.bzr')
        bazaar = Bazaar()

        with patch('bumpr.vcs.execute') as execute:
            execute.return_value = '\n'.join((' M modified.py', '? new.py'))
            with pytest.raises(BumprError):
                bazaar.validate()
            execute.assert_called_with('bzr status --short', verbose=False)

    def test_tag(self):
        bazaar = Bazaar()

        with patch.object(bazaar, 'execute') as execute:
            bazaar.tag('fake')
            execute.assert_called_with(['bzr', 'tag', 'fake'])

    def test_commit(self):
        bazaar = Bazaar()

        with patch.object(bazaar, 'execute') as execute:
            bazaar.commit('message')
            execute.assert_called_with(['bzr', 'commit', '-m', 'message'])

    def test_push(self):
        bazaar = Bazaar()

        with patch.object(bazaar, 'execute') as execute:
            bazaar.push()
            execute.assert_called_with(['bzr', 'push'])
