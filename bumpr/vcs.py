# -*- coding: utf-8 -*-
import subprocess

from bumpr import compat


class BaseVCS(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def execute(self, args):
        if self.verbose:
            subprocess.check_call(args)
        else:
            compat.check_output(args)

    def commit(self, message, files):
        raise NotImplementedError

    def tag(self, name):
        raise NotImplementedError


class Git(BaseVCS):
    def commit(self, message, files):
        for filename in files:
            self.execute(["git", "add", filename])
        self.execute(["git", "commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        self.execute(["git", "tag", name])


class Mercurial(BaseVCS):
    def commit(self, message, files):
        for filename in files:
            self.execute(["hg", "add", filename])
        self.execute(["hg", "commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        self.execute(["hg", "tag", name])


class Bazaar(BaseVCS):
    def commit(self, message, files):
        self.execute(["bzr"] + list(files) + ["commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        self.execute(["bzr", "tag", name])


VCS = {
    'git': Git,
    'hg': Mercurial,
    'bzr': Bazaar,
}
