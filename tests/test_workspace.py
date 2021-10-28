import os

import pytest


def test_workspace_fixture(workspace):
    assert str(workspace.root) == os.getcwd()
    assert workspace.version == "1.2.3.dev"
    assert workspace.module == workspace.root / "fake.py"
    with workspace.module.open() as module:
        assert workspace.version in module.read()
    assert workspace.readme == workspace.root / "README"
    with workspace.readme.open() as readme:
        assert workspace.version in readme.read()


@pytest.mark.version("2.3.4")
def test_workspace_fixture_with_version_override(workspace):
    assert workspace.version == "2.3.4"
    with workspace.module.open() as module:
        assert workspace.version in module.read()
    with workspace.readme.open() as readme:
        assert workspace.version in readme.read()
