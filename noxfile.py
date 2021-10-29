import os

import nox
from nox_poetry import Session, session

# nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = "3.7", "3.8", "3.9", "3.10"
ROOT = os.path.dirname(__file__)
TEST_DEPENDENCIES = [
    "mock",
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-sugar",
    "pytest-pythonpath",
]
DOC_DEPENDENCIES = [
    "sphinx",
    "sphinx-autobuild",
    "sphinx-rtd-theme",
]
CLEAN_PATTERNS = [
    "**/*.pyc",
    "**/__pycache__",
    "**/.pytest_cache",
    "**/,mypy_cache",
    "*.egg-info",
    ".cache",
    ".nox",
    "build",
    "dist",
    "docs/_build",
    "reports",
]

nox.options.sessions = "lint", "test", "doc"


@session
def clean(session: Session) -> None:
    """Cleanup all build artifacts"""
    session.cd(ROOT)
    for pattern in CLEAN_PATTERNS:
        session.run("rm", "-rf", pattern, external=True)


@session(python=PYTHON_VERSIONS)
def test(session: Session) -> None:
    """Run the test suite"""
    session.install(".[test]", *TEST_DEPENDENCIES)
    cmd = ["pytest"]
    posargs = session.posargs
    if session._runner.global_config.verbose:
        cmd.append("-v")
    if "--report" in session.posargs:
        posargs = [arg for arg in posargs if arg != "--report"]
        cmd.append("--junitxml=reports/tests.xml")
    session.run(*cmd, *posargs)


@session(python=PYTHON_VERSIONS)
def cover(session: Session) -> None:
    """Run tests suite with coverage"""
    session.install(".[test]", *TEST_DEPENDENCIES)
    cmd = [
        "pytest",
        "--cov-config=coverage.rc",
        "--cov-report=term",
        "--cov=bumpr",
    ]
    if session._runner.global_config.verbose:
        cmd.append("-v")
    if "--report" in session.posargs:
        cmd += [
            "--cov-report=html:{0}/reports/coverage".format(ROOT),
            "--cov-report=xml:{0}/reports/coverage.xml".format(ROOT),
            "--junitxml=reports/tests.xml",
        ]
    session.run(*cmd)


@session
def lint(session: Session) -> None:
    """Run the linter"""
    session.install(".[lint]", "flake8", "readme-renderer", "mypy")
    session.run("flake8", "bumpr")
    session.run("mypy", "bumpr")
    session.run("python", "-m", "readme_renderer", "README.rst", silent=True)


@session
def doc(session: Session) -> None:
    """Build the documentation"""
    session.install(".[doc]", *DOC_DEPENDENCIES)
    session.chdir("doc")
    session.run("sphinx-build", "-b", "html", ".", "build/html")
