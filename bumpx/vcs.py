import logging
from os.path import isdir
from typing import Optional

from .helpers import BumprError, execute

log = logging.getLogger(__name__)

MSG = "The current repository contains modified files"


class BaseVCS:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def execute(self, command: list[str]) -> None:
        """Execute a command"""
        execute(command, verbose=self.verbose)

    def validate(self, dryrun: bool = False) -> None:
        """Ensure the working dir is a repository and there is no modified files"""
        raise NotImplementedError

    def commit(self, message: str) -> None:
        """Commit all modified files"""
        raise NotImplementedError

    def tag(self, name: str, annotation: Optional[str] = None) -> None:
        """Create a tag"""
        raise NotImplementedError

    def push(self) -> None:
        """Push changes to remote repository"""
        raise NotImplementedError

    def gh_release(self, version: str, notes: str | None = None) -> None:
        if notes:
            self.execute(["gh", "release", "create", version, "--title", version, "--notes", notes])
        else:
            self.execute(["gh", "release", "create", version, "--title", version])


class Git(BaseVCS):
    def validate(self, dryrun: bool = False) -> None:
        if not isdir(".git"):
            raise BumprError("Current directory is not a git repopsitory")

        output: Optional[str] = execute("git status --porcelain", verbose=False)
        if output:
            for line in output.splitlines():
                if not line.startswith("??"):
                    if dryrun:
                        log.warning(MSG)
                        break
                    else:
                        raise BumprError(MSG)

    def commit(self, message: str) -> None:
        self.execute(["git", "commit", "-am", message])

    def tag(self, name: str, annotation: Optional[str] = None) -> None:
        cmd = ["git", "tag", name]
        if annotation:
            cmd += ["--annotate", "-m", '"{0}"'.format(annotation)]
        self.execute(cmd)

    def push(self) -> None:
        self.execute(["git", "push"])
        self.execute(["git", "push", "--tags"])


class Mercurial(BaseVCS):
    def validate(self, dryrun: bool = False) -> None:
        if not isdir(".hg"):
            raise BumprError("Current directory is not a mercurial repopsitory")

        output: Optional[str] = execute("hg status -mard", verbose=False)
        if output:
            for line in output.splitlines():
                if not line.startswith("??"):
                    if dryrun:
                        log.warning(MSG)
                        break
                    else:
                        raise BumprError(MSG)

    def commit(self, message: str) -> None:
        self.execute(["hg", "commit", "-A", "-m", message])

    def tag(self, name: str, annotation: Optional[str] = None) -> None:
        cmd = ["hg", "tag", name]
        if annotation:
            cmd += ["-m", '"{0}"'.format(annotation)]
        self.execute(cmd)

    def push(self) -> None:
        self.execute(["hg", "push"])


class Bazaar(BaseVCS):
    def validate(self, dryrun: bool = False) -> None:
        if not isdir(".bzr"):
            raise BumprError("Current directory is not a bazaar repopsitory")

        output: Optional[str] = execute("bzr status --short", verbose=False)
        if output:
            for line in output.splitlines():
                if not line.startswith("?"):
                    if dryrun:
                        log.warning(MSG)
                        break
                    else:
                        raise BumprError(MSG)

    def commit(self, message: str) -> None:
        self.execute(["bzr", "commit", "-m", message])

    def tag(self, name: str, annotation: Optional[str] = None) -> None:
        if annotation:
            log.warning("Tag annotation is not supported by Bazaar")
        self.execute(["bzr", "tag", name])

    def push(self) -> None:
        self.execute(["bzr", "push"])


class Fake(BaseVCS):
    def validate(self, dryrun: bool = False):
        return True


VCS = {
    "git": Git,
    "hg": Mercurial,
    "bzr": Bazaar,
    "fake": Fake,
}
