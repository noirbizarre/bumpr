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
    ".tox",
    "build",
    "dist",
    "docs/_build",
    "reports",
    "site",
]

LINTERS = (
    ("pyproject.toml validation", "poetry check"),
    ("Static Analysis", "ruff bumpr"),
    ("Type checking", "mypy bumpr"),
)
FORMATTERS = (
    ("Sort imports using isort", "isort"),
    ("Format code using black", "black"),
)


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
def lint(ctx):
    """Run linters"""
    header(lint.__doc__)
    with ctx.cd(ROOT):
        results = {}
        for name, cmd in LINTERS:
            info(name)
            result = results[name] = ctx.run(cmd, pty=PTY, warn=True)

            if result.failed:
                error(f"{name} failed")
            else:
                success(f"{name} succeeded")

        if any(r.failed for r in results.values()):
            exit("some linters failed")
        success("All linters succeeded")


@task
def format(ctx):
    """Format code"""
    header(format.__doc__)
    with ctx.cd(ROOT):
        for name, cmd in FORMATTERS:
            info(name)
            ctx.run(f"{cmd} *.py bumpr tests", pty=PTY, warn=True)


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


@task(clean, lint, test, doc, dist, default=True)
def all(ctx):
    """Run all tasks (default)"""
    pass
