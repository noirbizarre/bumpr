# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch

from tests.test_tools import workspace

from bumpr.vcs import BaseVCS, Git, Mercurial, Bazaar
from bumpr.helpers import BumprError


class BaseVCSTest(unittest.TestCase):
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


class GitTest(unittest.TestCase):
    def test_validate_ok(self):
        with workspace('git'):
            os.mkdir('.git')
            git = Git()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '?? new.py'
                git.validate()
                execute.assert_called_with('git status --porcelain', verbose=False)

    def test_validate_ko_not_git(self):
        with workspace('git'):
            git = Git()

            with patch('bumpr.vcs.execute') as execute:
                with self.assertRaises(BumprError):
                    git.validate()
                self.assertFalse(execute.called)

    def test_validate_ko_not_clean(self):
        with workspace('git'):
            os.mkdir('.git')
            git = Git()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
                with self.assertRaises(BumprError):
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


class MercurialTest(unittest.TestCase):
    def test_validate_ok(self):
        with workspace('mercurial'):
            os.mkdir('.hg')
            mercurial = Mercurial()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '?? new.py'
                mercurial.validate()
                execute.assert_called_with('hg status -mard', verbose=False)

    def test_validate_ko_not_mercurial(self):
        with workspace('mercurial'):
            mercurial = Mercurial()

            with patch('bumpr.vcs.execute') as execute:
                with self.assertRaises(BumprError):
                    mercurial.validate()
                self.assertFalse(execute.called)

    def test_validate_ko_not_clean(self):
        with workspace('mercurial'):
            os.mkdir('.hg')
            mercurial = Mercurial()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '\n'.join((' M modified.py', '?? new.py'))
                with self.assertRaises(BumprError):
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


class BazaarTest(unittest.TestCase):
    def test_validate_ok(self):
        with workspace('bazaar'):
            os.mkdir('.bzr')
            bazaar = Bazaar()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '? new.py'
                bazaar.validate()
                execute.assert_called_with('bzr status --short', verbose=False)

    def test_validate_ko_not_bazaar(self):
        with workspace('bazaar'):
            bazaar = Bazaar()

            with patch('bumpr.vcs.execute') as execute:
                with self.assertRaises(BumprError):
                    bazaar.validate()
                self.assertFalse(execute.called)

    def test_validate_ko_not_clean(self):
        with workspace('bazaar'):
            os.mkdir('.bzr')
            bazaar = Bazaar()

            with patch('bumpr.vcs.execute') as execute:
                execute.return_value = '\n'.join((' M modified.py', '? new.py'))
                with self.assertRaises(BumprError):
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
