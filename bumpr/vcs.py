# -*- coding: utf-8 -*-
import subprocess


class VCS(object):
    def commit(self, message, files):
        raise NotImplementedError

    def tag(self, name):
        raise NotImplementedError


class Git(VCS):
    def commit(self, message, files):
        for filename in files:
            subprocess.check_call(["git", "add", filename])
        subprocess.check_call(["git", "commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        subprocess.check_call(["git", "tag", name])


class Mercurial(VCS):
    def commit(self, message, files):
        for filename in files:
            subprocess.check_call(["hg", "add", filename])
        subprocess.check_call(["hg", "commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        subprocess.check_call(["hg", "tag", name])


class Bazaar(VCS):
    def commit(self, message, files):
        subprocess.check_call(["bzr"] + list(files) + ["commit", "-m", message.encode('utf-8')])

    def tag(self, name):
        subprocess.check_call(["bzr", "tag", name])
