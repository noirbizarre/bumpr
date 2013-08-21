# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

VERSION_PATTERN = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(\.(?P<suffix>[\w\d.]+))?')
SEMVER = r'{major}.{minor}.{patch}'
SEMVER_SUFFIXED = r'{major}.{minor}.{patch}.{suffix}'


class Version(object):
    MAJOR, MINOR, PATCH = range(3)

    def __init__(self, major=0, minor=0, patch=0, suffix=None):
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        self.suffix = suffix

    def bump(self, part=None, unsuffix=True, suffix=None):
        if part is Version.MAJOR:
            self.major += 1
            self.minor = 0
            self.patch = 0
        elif part is Version.MINOR:
            self.minor += 1
            self.patch = 0
        elif part is Version.PATCH:
            self.patch += 1

        if unsuffix:
            self.suffix = None
        if suffix:
            self.suffix = suffix

        return self

    def copy(self, unsuffix=False):
        version = Version(**self.__dict__)
        if unsuffix:
            version.suffix = None
        return version

    def __unicode__(self):
        pattern = SEMVER_SUFFIXED if self.suffix else SEMVER
        return pattern.format(**self.__dict__)

    @classmethod
    def parse(cls, string):
        match = VERSION_PATTERN.match(string)
        return cls(**match.groupdict())

    __str__ = __unicode__


PARTS = {
    'major': Version.MAJOR,
    'minor': Version.MINOR,
    'patch': Version.PATCH,
}
