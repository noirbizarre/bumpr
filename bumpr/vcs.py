from __future__ import annotations

import logging
from os.path import isdir

from .helpers import BumprError, execute

log = logging.getLogger(__name__)

MSG = "The current repository contains modified files"


class BaseVCS:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def execute(self, command):
        """Execute a command"""
        execute(command, verbose=self.verbose)

    def validate(self, dryrun=False):
        """Ensure the working dir is a repository and there is no modified files"""
        raise NotImplementedError

    def commit(self, message):
        """Commit all modified files"""
        raise NotImplementedError

    def tag(self, name, annotation=None):
        """Create a tag"""
        raise NotImplementedError

    def push(self):
        """Push changes to remote repository"""
        raise NotImplementedError


class Git(BaseVCS):
    def validate(self, dryrun=False):
        if not isdir(".git"):
            raise BumprError("Current directory is not a git repopsitory")

        for line in execute("git status --porcelain", verbose=False).splitlines():
            if not line.startswith("??"):
                if dryrun:
                    log.warning(MSG)
                    break
                else:
                    raise BumprError(MSG)

    def commit(self, message):
        self.execute(["git", "commit", "-am", message])

    def tag(self, name, annotation=None):
        cmd = ["git", "tag", name]
        if annotation:
            cmd += ["--annotate", "-m", '"{0}"'.format(annotation)]
        self.execute(cmd)

    def push(self):
        self.execute(["git", "push"])
        self.execute(["git", "push", "--tags"])


class Mercurial(BaseVCS):
    def validate(self, dryrun=False):
        if not isdir(".hg"):
            raise BumprError("Current directory is not a mercurial repopsitory")

        for line in execute("hg status -mard", verbose=False).splitlines():
            if not line.startswith("??"):
                if dryrun:
                    log.warning(MSG)
                    break
                else:
                    raise BumprError(MSG)

    def commit(self, message):
        self.execute(["hg", "commit", "-A", "-m", message])

    def tag(self, name, annotation=None):
        cmd = ["hg", "tag", name]
        if annotation:
            cmd += ["-m", '"{0}"'.format(annotation)]
        self.execute(cmd)

    def push(self):
        self.execute(["hg", "push"])


class Bazaar(BaseVCS):
    def validate(self, dryrun=False):
        if not isdir(".bzr"):
            raise BumprError("Current directory is not a bazaar repopsitory")

        for line in execute("bzr status --short", verbose=False).splitlines():
            if not line.startswith("?"):
                if dryrun:
                    log.warning(MSG)
                    break
                else:
                    raise BumprError(MSG)

    def commit(self, message):
        self.execute(["bzr", "commit", "-m", message])

    def tag(self, name, annotation=None):
        if annotation:
            log.warning("Tag annotation is not supported by Bazaar")
        self.execute(["bzr", "tag", name])

    def push(self):
        self.execute(["bzr", "push"])


class Fake(BaseVCS):
    def validate(self, dryrun=False):
        return True


VCS = {
    "git": Git,
    "hg": Mercurial,
    "bzr": Bazaar,
    "fake": Fake,
}
