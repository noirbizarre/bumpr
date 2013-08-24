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

from bumpr.config import Config, ObjectDict
from bumpr.helpers import execute


@contextmanager
def workspace(module_name='fake', version='1.2.3.dev'):
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


class WorkspaceTest(unittest.TestCase):
    def test_behavior(self):
        initial_dir = os.getcwd()
        with workspace('fake') as wksp:
            self.assertNotEqual(os.getcwd(), initial_dir)
            self.assertEqual(wksp.root, os.getcwd())
            self.assertEqual(wksp.module, join(wksp.root, 'fake.py'))
            self.assertEqual(wksp.readme, join(wksp.root, 'README'))
        self.assertEqual(os.getcwd(), initial_dir)
