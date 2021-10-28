import os

import nox

from nox_poetry import session, Session

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

nox.options.sessions = "lint", "test", "doc"


@session(python=PYTHON_VERSIONS)
def test(session: Session) -> None:
    """Run the test suite"""
    session.install(".[test]", *TEST_DEPENDENCIES)
    session.run("pytest", *session.posargs)


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
