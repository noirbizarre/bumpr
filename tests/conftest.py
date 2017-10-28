# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import shutil
import tempfile
import sys

from textwrap import dedent

import pytest


def pytest_configure():
    from bumpr import log
    log.init()


DEFAULT_VERSION = '1.2.3.dev'


class Workspace(object):
    def __init__(self, version):
        self.module_name = 'fake'
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp(self.module_name)
        self.version = version
        self.module_filename = self.write('{0}.py'.format(self.module_name), '''\
            # -*- coding: utf-8 -*-

            __version__ = '{version}'
        ''')
        self.readme_filename = self.write('README', '''\
            README

            Version: {version}
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Non, ad, facilis, vel voluptas fugiat sit debitis iusto
            numquam quasi aliquid cum quod laborum assumenda quia
        ''')

    def write(self, filename, content):
        wksp_filename = os.path.join(self.root, filename)
        with open(wksp_filename, 'wb') as f:
            content = dedent(content).format(**self.__dict__)
            f.write(content.encode('utf8'))
        return wksp_filename

    def mkdir(self, dirname):
        wksp_dirname = os.path.join(self.root, dirname)
        try:
            os.makedirs(wksp_dirname)
        except FileExistsError as exc:
            pass

    def chdir(self):
        os.chdir(self.root)

    def cleanup(self):
        os.chdir(self.cwd)
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        if self.root in sys.path:
            sys.path.remove(self.root)


@pytest.fixture
def workspace(request):
    marker = request.node.get_marker('version')
    version = marker.args[0] if marker else DEFAULT_VERSION
    wksp = Workspace(version)
    wksp.chdir()

    yield wksp

    wksp.cleanup()
