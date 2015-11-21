# -*- coding: utf-8 -*-
from os.path import isdir

from bumpr.helpers import execute, BumprError


class BaseVCS(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def execute(self, command):
        '''Execute a command'''
        execute(command, verbose=self.verbose)

    def validate(self):
        '''Ensure the working dir is a repository and there is no modified files'''
        raise NotImplementedError

    def commit(self, message):
        '''Commit all modified files'''
        raise NotImplementedError

    def tag(self, name):
        '''Create a tag'''
        raise NotImplementedError


class Git(BaseVCS):
    def validate(self):
        if not isdir('.git'):
            raise BumprError('Current directory is not a git repopsitory')

        for line in execute('git status --porcelain', verbose=False).splitlines():
            if not line.startswith('??'):
                raise BumprError('The current repository contains modified files')

    def commit(self, message):
        self.execute(["git", "commit", "-am", message])

    def tag(self, name):
        self.execute(["git", "tag", name])


class Mercurial(BaseVCS):
    def validate(self):
        if not isdir('.hg'):
            raise BumprError('Current directory is not a mercurial repopsitory')

        for line in execute('hg status -mard', verbose=False).splitlines():
            if not line.startswith('??'):
                raise BumprError('The current repository contains modified files')

    def commit(self, message):
        self.execute(["hg", "commit", "-A", "-m", message])

    def tag(self, name):
        self.execute(["hg", "tag", name])


class Bazaar(BaseVCS):
    def validate(self):
        if not isdir('.bzr'):
            raise BumprError('Current directory is not a bazaar repopsitory')

        for line in execute('bzr status --short', verbose=False).splitlines():
            if not line.startswith('?'):
                raise BumprError('The current repository contains modified files')

    def commit(self, message):
        self.execute(["bzr", "commit", "-m", message])

    def tag(self, name):
        self.execute(["bzr", "tag", name])


class Fake(BaseVCS):
    def validate(self):
        return True

    def commit(self, message):
        pass

    def tag(self, name):
        pass


VCS = {
    'git': Git,
    'hg': Mercurial,
    'bzr': Bazaar,
    'fake': Fake,
}
