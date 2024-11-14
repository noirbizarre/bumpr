import logging

from .helpers import execute

log = logging.getLogger(__name__)


class BaseForge:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def execute(self, command: list[str]) -> None:
        """Execute a command"""
        execute(command, verbose=self.verbose)

    def release(self, version: str, notes: str | None = None) -> None:
        """Create a release on the forge"""
        raise NotImplementedError


class GitHub(BaseForge):
    def release(self, version: str, notes: str | None = None) -> None:
        if notes:
            self.execute(["gh", "release", "create", version, "--title", version, "--notes", notes])
        else:
            self.execute(["gh", "release", "create", version, "--title", version])


class GitLab(BaseForge):
    pass


FORGES = {
    "github": GitHub,
    "gitlab": GitLab,
}
