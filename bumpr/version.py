from __future__ import annotations

import re


class Version:
    MAJOR, MINOR, PATCH = range(3)

    PATTERN = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(\.(?P<suffix>[\w\d.]+))?")
    FORMAT = r"{major}.{minor}.{patch}"
    FORMAT_SUFFIXED = r"{major}.{minor}.{patch}.{suffix}"

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

    def copy(self, **kwargs):
        version = Version(**self.__dict__)
        unsuffix = kwargs.pop("unsuffix", False)
        version.bump(unsuffix=unsuffix, **kwargs)
        return version

    def __unicode__(self):
        pattern = self.FORMAT_SUFFIXED if self.suffix else self.FORMAT
        return pattern.format(**self.__dict__)

    @classmethod
    def parse(cls, string):
        match = cls.PATTERN.match(string)
        return cls(**match.groupdict())

    __str__ = __unicode__

    def __repr__(self):
        return "'Version({major},{minor},{patch},{suffix})'".format(**self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False
        return self.__dict__ == other.__dict__


PARTS = {
    "major": Version.MAJOR,
    "minor": Version.MINOR,
    "patch": Version.PATCH,
}
