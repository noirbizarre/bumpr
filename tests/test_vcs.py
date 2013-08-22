# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch, call

from bumpr.vcs import BaseVCS, Git, Mercurial, Bazaar

class BaseVCSTest(unittest.TestCase):
    def test_execute_verbose(self):
        vcs = BaseVCS(verbose=True)
        with patch('subprocess.check_call') as check_call:
            with patch('bumpr.compat.check_output') as check_output:
                vcs.execute(['cmd', 'arg'])
                check_call.assert_called_with(['cmd', 'arg'])
                self.assertFalse(check_output.called)

    def test_execute_quiet(self):
        vcs = BaseVCS(verbose=False)
        with patch('subprocess.check_call') as check_call:
            with patch('bumpr.compat.check_output') as check_output:
                vcs.execute(['cmd', 'arg'])
                check_output.assert_called_with(['cmd', 'arg'])
                self.assertFalse(check_call.called)


class GitTest(unittest.TestCase):
    def test_tag(self):
        git = Git()

        with patch.object(git, 'execute') as execute:
            git.tag('fake')
            execute.assert_called_with(['git', 'tag', 'fake'])

    def test_commit(self):
        git = Git()

        with patch.object(git, 'execute') as execute:
            git.commit('message', ['file1', 'file2'])

            expected = (
                call(['git', 'add', 'file1']),
                call(['git', 'add', 'file2']),
                call(['git', 'commit', '-m', 'message'.encode('utf8')]),
            )
            self.assertSequenceEqual(execute.call_args_list, expected)


class MercurialTest(unittest.TestCase):
    def test_tag(self):
        mercurial = Mercurial()

        with patch.object(mercurial, 'execute') as execute:
            mercurial.tag('fake')
            execute.assert_called_with(['hg', 'tag', 'fake'])

    def test_commit(self):
        mercurial = Mercurial()

        with patch.object(mercurial, 'execute') as execute:
            mercurial.commit('message', ['file1', 'file2'])

            expected = (
                call(['hg', 'add', 'file1']),
                call(['hg', 'add', 'file2']),
                call(['hg', 'commit', '-m', 'message'.encode('utf8')]),
            )
            self.assertSequenceEqual(execute.call_args_list, expected)


class BazaarTest(unittest.TestCase):
    def test_tag(self):
        bazaar = Bazaar()

        with patch.object(bazaar, 'execute') as execute:
            bazaar.tag('fake')
            execute.assert_called_with(['bzr', 'tag', 'fake'])

    def test_commit(self):
        bazaar = Bazaar()

        with patch.object(bazaar, 'execute') as execute:
            bazaar.commit('message', ['file1', 'file2'])
            execute.assert_called_with(['bzr', 'file1', 'file2', 'commit', '-m', 'message'.encode('utf8')])
