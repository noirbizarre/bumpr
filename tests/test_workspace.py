# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os

import pytest


def test_workspace_fixture(workspace):
    assert workspace.root == os.getcwd()
    assert workspace.root != workspace.cwd
    assert workspace.version == '1.2.3.dev'
    assert workspace.module_filename == os.path.join(workspace.root, 'fake.py')
    with open(workspace.module_filename) as module:
        assert workspace.version in module.read()
    assert workspace.readme_filename == os.path.join(workspace.root, 'README')
    with open(workspace.readme_filename) as readme:
        assert workspace.version in readme.read()
    workspace.cleanup()
    assert workspace.cwd == os.getcwd()


@pytest.mark.version('2.3.4')
def test_workspace_fixture_with_version_override(workspace):
    assert workspace.version == '2.3.4'
    with open(workspace.module_filename) as module:
        assert workspace.version in module.read()
    with open(workspace.readme_filename) as readme:
        assert workspace.version in readme.read()
