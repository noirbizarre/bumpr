import os
import sys

from invoke import task

PTY = sys.platform != "win32"
ROOT = os.path.dirname(__file__)

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


def color(code):
    """A simple ANSI color wrapper factory"""
    return lambda t: "\033[{0}{1}\033[0;m".format(code, t)


green = color("1;32m")
red = color("1;31m")
blue = color("1;30m")
cyan = color("1;36m")
purple = color("1;35m")
white = color("1;39m")


def header(text):
    """Display an header"""
    print(" ".join((blue(">>"), cyan(text))))
    sys.stdout.flush()


def info(text, *args, **kwargs):
    """Display informations"""
    text = text.format(*args, **kwargs)
    print(" ".join((purple(">>>"), text)))
    sys.stdout.flush()


def success(text):
    """Display a success message"""
    print(" ".join((green("✔"), white(text))))
    sys.stdout.flush()


def error(text):
    """Display an error message"""
    print(red("✘ {0}".format(text)))
    sys.stdout.flush()


def exit(text=None, code=-1):
    if text:
        error(text)
    sys.exit(code)


@task
def clean(ctx):
    """Cleanup all build artifacts"""
    header(clean.__doc__)
    with ctx.cd(ROOT):
        for pattern in CLEAN_PATTERNS:
            info(pattern)
            ctx.run("rm -rf {0}".format(" ".join(CLEAN_PATTERNS)))


@task
def deps(ctx):
    """Install or update development dependencies"""
    header(deps.__doc__)
    with ctx.cd(ROOT):
        ctx.run("pip install -r requirements/develop.pip -r requirements/doc.pip", pty=PTY)


@task
def test(ctx, report=False, verbose=False):
    """Run tests suite"""
    header(test.__doc__)
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")
    if report:
        cmd.append("--junitxml=reports/tests.xml")
    with ctx.cd(ROOT):
        ctx.run(" ".join(cmd), pty=PTY)


@task
def cover(ctx, report=False, verbose=False):
    """Run tests suite with coverage"""
    header(cover.__doc__)
    cmd = [
        "pytest",
        "--cov-report=term",
        "--cov=bumpr",
    ]
    if verbose:
        cmd.append("-v")
    if report:
        cmd += [
            "--cov-report=html:{0}/reports/coverage".format(ROOT),
            "--cov-report=xml:{0}/reports/coverage.xml".format(ROOT),
            "--junitxml=reports/tests.xml",
        ]
    with ctx.cd(ROOT):
        ctx.run(" ".join(cmd), pty=PTY)


@task
def qa(ctx):
    """Run a quality report"""
    header(qa.__doc__)
    with ctx.cd(ROOT):
        info("Python Static Analysis")
        flake8_results = ctx.run("flake8 bumpr", pty=PTY, warn=True)
        if flake8_results.failed:
            error("There is some lints to fix")
        else:
            success("No lint to fix")
        info("Type checking")
        mypy_results = ctx.run("mypy bumpr", pty=PTY, warn=True)
        if mypy_results.failed:
            print(mypy_results.stdout)
            error("There is some typing to fix")
        else:
            success("Typing is correct")
    if flake8_results.failed or mypy_results.failed:
        exit("Quality check failed", flake8_results.return_code or mypy_results.return_code)
    success("Quality check OK")


@task
def tox(ctx):
    """Run test in all Python versions"""
    header(tox.__doc__)
    ctx.run("tox", pty=PTY)


@task
def doc(ctx, serve=False):
    """Build the documentation"""
    header(doc.__doc__)
    with ctx.cd(ROOT):
        if serve:
            ctx.run("mkdocs serve")
        else:
            ctx.run("mkdocs build", pty=PTY)
            success("Documentation available in site/")


@task
def completion(ctx):
    """Generate bash completion script"""
    header(completion.__doc__)
    with ctx.cd(ROOT):
        ctx.run("_bumpr_COMPLETE=source bumpr > bumpr-complete.sh", pty=PTY)
    success("Completion generated in bumpr-complete.sh")


@task
def dist(ctx):
    """Package for distribution"""
    header(dist.__doc__)
    with ctx.cd(ROOT):
        ctx.run("poetry build", pty=PTY)
    success("Distribution is available in dist directory")


@task(clean, test, qa, doc, dist, default=True)
def all(ctx):
    """Run all tasks (default)"""
    pass
