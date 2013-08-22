# -*- coding: utf-8 -*-
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
from mock import patch, MagicMock
from textwrap import dedent

from bumpr.config import Config, ObjectDict
from bumpr.releaser import Releaser, HOOKS
from bumpr.version import Version


@contextmanager
def workspace(module_name, version='1.2.3.dev'):
    root = tempfile.mkdtemp(module_name)
    module_filename = join(root, '{0}.py'.format(module_name))
    module_content =  '''\
        # -*- coding: utf-8 -*-

        __version__ = '{version}'
        '''
    readme_filename = join(root, 'README')
    readme_content = '''\
        README

        Version: {version}
        Lorem ipsum dolor sit amet, consectetur adipisicing elit.
        Non, ad, facilis, vel voluptas fugiat sit debitis iusto
        numquam quasi aliquid cum quod laborum assumenda quia
        '''

    for filename, content in ((module_filename, module_content), (readme_filename, readme_content)):
        with open(filename, 'wb') as f:
            content = dedent(content).format(version=version)
            f.write(content.encode('utf8'))

    cwd = os.getcwd()
    os.chdir(root)

    yield ObjectDict({
        'root': root,
        'module': module_filename,
        'readme': readme_filename,
    })

    os.chdir(cwd)
    shutil.rmtree(root)
    if root in sys.path:
        sys.path.remove(root)


def test_workspace():
    initial_dir = os.getcwd()
    with workspace('fake') as wksp:
        self.assertNotEqual(os.getcwd(), initial_dir)
        self.assertEqual(wksp.root, os.getcwd())
        self.assertEqual(wksp.module, join(w.root, 'fake.py'))
        self.assertEqual(wksp.readme, join(w.root, 'README'))
    self.assertEqual(os.getcwd(), initial_dir)


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

        self.assertEqual(releaser.modified, set())
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

        with patch.object(releaser, 'execute') as mock:
            releaser.test()
            mock.assert_called_with('test command')

    def test_publish(self):
        config = Config({
            'file': 'fake.py',
            'publish': 'publish command',
        })

        with workspace('fake'):
            releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.publish()
            mock.assert_called_with('publish command', False)

    def test_publish_dryrun(self):
        config = Config({
            'file': 'fake.py',
            'publish': 'publish command',
            'dryrun': True,
        })

        with workspace('fake'):
            releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.publish()
            mock.assert_called_with('publish command', True)

    def test_clean(self):
        config = Config({
            'file': 'fake.py',
            'clean': 'clean command',
        })
        with workspace('fake'):
            releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.clean()
            mock.assert_called_with('clean command')

    def test_execute_verbose(self):
        config = Config({'file': 'fake.py', 'verbose': True})
        with workspace('fake') as wksp:
            releaser = Releaser(config)

        with patch('subprocess.check_call') as check_call:
            releaser.execute('bumpr test {major}.{minor}')
            check_call.assert_called_with(['bumpr', 'test', '1.2'])

    def test_execute_quiet(self):
        config = Config({'file': 'fake.py'})
        with workspace('fake') as wksp:
            releaser = Releaser(config)

        with patch('bumpr.compat.check_output') as check_call:
            releaser.execute('bumpr test {major}.{minor}')
            check_call.assert_called_with(['bumpr', 'test', '1.2'])

    def test_commit(self):
        config = Config({'file': 'fake.py', 'vcs': 'git'})
        with workspace('fake') as wksp:
            releaser = Releaser(config)

        with patch.object(releaser, 'vcs') as vcs:
            releaser.commit('message')
            vcs.commit.assert_called_with('message', set())

    def test_release_wihtout_vcs_or_commands(self):
        with workspace('fake', '1.2.3.dev') as wksp:
            config = Config({'file': 'fake.py', 'files': [wksp.readme]})
            releaser = Releaser(config)
            with patch.object(releaser, 'execute') as execute:
                with patch.object(releaser, 'prepare') as prepare:
                    releaser.release()
                    self.assertFalse(execute.called)
                    self.assertFalse(prepare.called)

            for filename in wksp.module, wksp.readme:
                with open(filename) as f:
                    content = f.read()
                    self.assertIn('1.2.3', content)
                    self.assertNotIn('1.2.3.dev', content)


    def test_prepare(self):
        pass
