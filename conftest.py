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
    log.declare()


class Workspace(object):
    def __init__(self, module_name='fake', version='1.2.3.dev'):
        self.module_name = module_name
        self.cwd = os.getcwd()
        self.root = tempfile.mkdtemp(module_name)
        self.version = version
        self.module_filename = self.write('{0}.py'.format(module_name), '''\
            # -*- coding: utf-8 -*-

            __version__ = '{version}'
            '''
        )
        self.readme_filename = self.write('README', '''\
            README

            Version: {version}
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Non, ad, facilis, vel voluptas fugiat sit debitis iusto
            numquam quasi aliquid cum quod laborum assumenda quia
            '''
        )

    def write(self, filename, content):
        wksp_filename = os.path.join(self.root, filename)
        with open(wksp_filename, 'wb') as f:
            content = dedent(content).format(**self.__dict__)
            f.write(content.encode('utf8'))
        return wksp_filename

    def chdir(self):
        os.chdir(self.root)

    def cleanup(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.root)
        if self.root in sys.path:
            sys.path.remove(self.root)


def with_workspace(module_name='fake', version='1.2.3.dev'):
    def wrapper(wrapped):
        wrapped.__module_name = module_name
        wrapped.__version = version
        return wrapped
    return wrapper


@pytest.fixture
def workspace(request):
    wksp = Workspace()
    wksp.chdir()

    yield wksp

    wksp.cleanup()
