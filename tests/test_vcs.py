# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

import pytest

from bumpr.vcs import BaseVCS, Git, Mercurial, Bazaar
from bumpr.helpers import BumprError


class BaseVCSTest(object):
    def test_execute_verbose(self, mocker):
        vcs = BaseVCS(verbose=True)
        execute = mocker.patch('bumpr.vcs.execute')
        vcs.execute('cmd arg')
        execute.assert_called_with('cmd arg', verbose=True)

    def test_execute_quiet(self, mocker):
        vcs = BaseVCS(verbose=False)
        execute = mocker.patch('bumpr.vcs.execute')
        vcs.execute('cmd arg')
        execute.assert_called_with('cmd arg', verbose=False)


class GitTest(object):
    def test_validate_ok(self, workspace, mocker):
        workspace.mkdir('.git')
        git = Git()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '?? new.py'
        git.validate()
        execute.assert_called_with('git status --porcelain', verbose=False)

    def test_validate_ko_not_git(self, workspace, mocker):
        git = Git()

        execute = mocker.patch('bumpr.vcs.execute')
        with pytest.raises(BumprError):
            git.validate()
        assert execute.called is False

    def test_validate_ko_not_clean(self, workspace, mocker):
        workspace.mkdir('.git')
        git = Git()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
        with pytest.raises(BumprError):
            git.validate()
        execute.assert_called_with('git status --porcelain', verbose=False)

    def test_validate_not_clean_dryrun(self, workspace, mocker):
        workspace.mkdir('.git')
        git = Git()
        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '?? new.py'))

        git.validate(dryrun=True)

        execute.assert_called_with('git status --porcelain', verbose=False)

    def test_tag(self, mocker):
        git = Git()

        execute = mocker.patch.object(git, 'execute')
        git.tag('fake')
        execute.assert_called_with(['git', 'tag', 'fake'])

    def test_tag_annotate(self, mocker):
        git = Git()

        execute = mocker.patch.object(git, 'execute')
        git.tag('fake', annotation='some annotation')
        execute.assert_called_with(['git', 'tag', 'fake', '--annotate', '-m', '"some annotation"'])

    def test_commit(self, mocker):
        git = Git()

        execute = mocker.patch.object(git, 'execute')
        git.commit('message')
        execute.assert_called_with(['git', 'commit', '-am', 'message'])

    def test_push(self, mocker):
        git = Git()

        execute = mocker.patch.object(git, 'execute')
        git.push()
        execute.assert_any_call(['git', 'push'])
        execute.assert_any_call(['git', 'push', '--tags'])


class MercurialTest(object):
    def test_validate_ok(self, workspace, mocker):
        workspace.mkdir('.hg')
        mercurial = Mercurial()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '?? new.py'
        mercurial.validate()
        execute.assert_called_with('hg status -mard', verbose=False)

    def test_validate_ko_not_mercurial(self, workspace, mocker):
        mercurial = Mercurial()

        execute = mocker.patch('bumpr.vcs.execute')
        with pytest.raises(BumprError):
            mercurial.validate()
        assert execute.called is False

    def test_validate_ko_not_clean(self, workspace, mocker):
        workspace.mkdir('.hg')
        mercurial = Mercurial()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
        with pytest.raises(BumprError):
            mercurial.validate()
        execute.assert_called_with('hg status -mard', verbose=False)

    def test_validate_not_clean_dryrun(self, workspace, mocker):
        workspace.mkdir('.hg')
        mercurial = Mercurial()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
        mercurial.validate(dryrun=True)
        execute.assert_called_with('hg status -mard', verbose=False)

    def test_tag(self, mocker):
        mercurial = Mercurial()

        execute = mocker.patch.object(mercurial, 'execute')
        mercurial.tag('fake')
        execute.assert_called_with(['hg', 'tag', 'fake'])

    def test_tag_annotate(self, mocker):
        mercurial = Mercurial()

        execute = mocker.patch.object(mercurial, 'execute')
        mercurial.tag('fake', annotation='some annotation')
        execute.assert_called_with(['hg', 'tag', 'fake', '-m', '"some annotation"'])

    def test_commit(self, mocker):
        mercurial = Mercurial()

        execute = mocker.patch.object(mercurial, 'execute')
        mercurial.commit('message')
        execute.assert_called_with(['hg', 'commit', '-A', '-m', 'message'])

    def test_push(self, mocker):
        mercurial = Mercurial()

        execute = mocker.patch.object(mercurial, 'execute')
        mercurial.push()
        execute.assert_called_with(['hg', 'push'])


class BazaarTest(object):
    def test_validate_ok(self, workspace, mocker):
        workspace.mkdir('.bzr')
        bazaar = Bazaar()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '? new.py'
        bazaar.validate()
        execute.assert_called_with('bzr status --short', verbose=False)

    def test_validate_ko_not_bazaar(self, workspace, mocker):
        bazaar = Bazaar()

        execute = mocker.patch('bumpr.vcs.execute')
        with pytest.raises(BumprError):
            bazaar.validate()
        assert execute.called is False

    def test_validate_ko_not_clean(self, workspace, mocker):
        workspace.mkdir('.bzr')
        bazaar = Bazaar()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '? new.py'))
        with pytest.raises(BumprError):
            bazaar.validate()
        execute.assert_called_with('bzr status --short', verbose=False)

    def test_validate_not_clean_dryrun(self, workspace, mocker):
        workspace.mkdir('.bzr')
        bazaar = Bazaar()

        execute = mocker.patch('bumpr.vcs.execute')
        execute.return_value = '\n'.join((' M modified.py', '? new.py'))

        bazaar.validate(dryrun=True)

        execute.assert_called_with('bzr status --short', verbose=False)

    def test_tag(self, mocker, caplog):
        bazaar = Bazaar()

        execute = mocker.patch.object(bazaar, 'execute')
        bazaar.tag('fake')
        execute.assert_called_with(['bzr', 'tag', 'fake'])

    def test_tag_annotate(self, mocker, caplog):
        bazaar = Bazaar()

        execute = mocker.patch.object(bazaar, 'execute')
        bazaar.tag('fake', annotation='some annotation')
        execute.assert_called_with(['bzr', 'tag', 'fake'])

        record = caplog.record_tuples[0]

        assert record[0] == 'bumpr.vcs'
        assert record[1] == logging.WARNING

    def test_commit(self, mocker):
        bazaar = Bazaar()

        execute = mocker.patch.object(bazaar, 'execute')
        bazaar.commit('message')
        execute.assert_called_with(['bzr', 'commit', '-m', 'message'])

    def test_push(self, mocker):
        bazaar = Bazaar()

        execute = mocker.patch.object(bazaar, 'execute')
        bazaar.push()
        execute.assert_called_with(['bzr', 'push'])
