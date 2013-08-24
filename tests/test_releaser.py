# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import shutil
import tempfile
import sys

try:
    import unittest2 as unittest
except:
    import unittest

from os.path import join, relpath
from contextlib import contextmanager
from mock import patch, MagicMock, ANY
from textwrap import dedent

from tests.test_tools import workspace

from bumpr.config import Config, ObjectDict
from bumpr.helpers import execute
from bumpr.releaser import Releaser, HOOKS
from bumpr.version import Version



class ReleaserTest(unittest.TestCase):
    def test_constructor(self):
        config = Config({
            'file': 'fake.py'
        })
        with workspace('fake', '1.2.3.dev') as wksp:
            releaser = Releaser(config)

        self.assertIsInstance(releaser.prev_version, Version)
        self.assertEqual(str(releaser.prev_version), '1.2.3.dev')

        self.assertIsInstance(releaser.version, Version)
        self.assertIsInstance(releaser.next_version, Version)

        self.assertIsNone(releaser.timestamp)

        self.assertFalse(hasattr(releaser, 'vcs'))
        self.assertFalse(hasattr(releaser, 'diffs'))

        self.assertEqual(releaser.hooks, [])

    def test_constructor_with_hooks(self):
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

        with workspace('fake', '1.2.3.dev') as wksp:
            with patch('bumpr.releaser.HOOKS', hooks) as mock:
                releaser = Releaser(config)
                for hook in hooks:
                    hook.assert_called_with(releaser)

    def test_test(self):
        config = Config({
            'file': 'fake.py',
            'tests': 'test command',
        })
        with workspace('fake'):
            releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.test()
            execute.assert_called_with('test command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_publish(self):
        config = Config({
            'file': 'fake.py',
            'publish': 'publish command',
        })

        with workspace('fake'):
            releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.publish()
            execute.assert_called_with('publish command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_clean(self):
        config = Config({
            'file': 'fake.py',
            'clean': 'clean command',
        })
        with workspace('fake'):
            releaser = Releaser(config)

        with patch('bumpr.releaser.execute') as execute:
            releaser.clean()
            execute.assert_called_with('clean command', replacements=ANY, dryrun=ANY, verbose=ANY)

    def test_commit(self):
        config = Config({'file': 'fake.py', 'vcs': 'fake'})
        with workspace('fake') as wksp:
            releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.commit('message')
            vcs.commit.assert_called_with('message')

    def test_tag(self):
        config = Config({'file': 'fake.py', 'vcs': 'fake'})
        with workspace('fake') as wksp:
            releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.tag()
            vcs.tag.assert_called_with(str(releaser.version))

    def test_release_wihtout_vcs_or_commands(self):
        with workspace('fake', '1.2.3.dev') as wksp:
            config = Config({'file': 'fake.py', 'files': [wksp.readme]})
            releaser = Releaser(config)
            with patch('bumpr.releaser.execute') as execute:
                with patch.object(releaser, 'commit') as commit:
                    releaser.release()
                    self.assertFalse(execute.called)
                    self.assertFalse(commit.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.3', content)
                    self.assertNotIn('1.2.3.dev', content)

    def test_bump(self):
        with workspace('fake', '1.2.3.dev') as wksp:
            config = Config({'file': 'fake.py', 'files': [wksp.readme]})
            releaser = Releaser(config)
            with patch.object(releaser, 'commit') as commit:
                with patch.object(releaser, 'tag') as tag:
                    releaser.bump()
                    self.assertFalse(commit.called)
                    self.assertFalse(tag.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.3', content)
                    self.assertNotIn('1.2.3.dev', content)

    def test_bump_vcs(self):
        with workspace('fake', '1.2.3.dev') as wksp:
            config = Config({
                'file': 'fake.py',
                'files': [wksp.readme],
                'vcs': 'fake',
            })
            releaser = Releaser(config)
            with patch.object(releaser, 'commit') as commit:
                with patch.object(releaser, 'tag') as tag:
                    releaser.bump()
                    self.assertEqual(commit.call_count, 1)
                    self.assertTrue(tag.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.3', content)
                    self.assertNotIn('1.2.3.dev', content)

    def test_release_dryrun(self):
        with workspace('fake', '1.2.3.dev') as wksp:
            config = Config({
                'file': 'fake.py',
                'files': [wksp.readme],
                'vcs': 'fake',
                'dryrun': True,
            })
            releaser = Releaser(config)
            with patch('bumpr.releaser.execute') as execute:
                with patch.object(releaser, 'vcs') as vcs:
                    releaser.release()
                    self.assertFalse(execute.called)
                    self.assertFalse(vcs.commit.called)
                    self.assertFalse(vcs.tag.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.3.dev', content)
                    self.assertNotIn('1.2.4', content)

    def test_prepare(self):
        with workspace('fake', '1.2.3') as wksp:
            config = Config({
                'file': 'fake.py',
                'files': [wksp.readme],
                'prepare': {
                    'part': Version.PATCH,
                    'suffix': 'dev',
                }
            })
            releaser = Releaser(config)
            with patch.object(releaser, 'commit') as commit:
                with patch.object(releaser, 'tag') as tag:
                    releaser.prepare()
                    self.assertFalse(commit.called)
                    self.assertFalse(tag.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.4.dev', content)
                    self.assertNotIn('1.2.3', content)

    def test_prepare_vcs(self):
        with workspace('fake', '1.2.3') as wksp:
            config = Config({
                'file': 'fake.py',
                'files': [wksp.readme],
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
                    self.assertEqual(commit.call_count, 1)
                    self.assertFalse(tag.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.4.dev', content)
                    self.assertNotIn('1.2.3', content)
