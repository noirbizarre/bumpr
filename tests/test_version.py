# -*- coding: utf-8 -*-
import sys

try:
    import unittest2 as unittest
except:
    import unittest

from bumpr.version import  Version


class VersionTest(unittest.TestCase):
    def test_default_constructor(self):
        version = Version()

        self.assertEqual(version.major, 0)
        self.assertEqual(version.minor, 0)
        self.assertEqual(version.patch, 0)
        self.assertEqual(version.suffix, None)

    def test_constructor(self):
        version = Version(1, suffix='dev')

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 0)
        self.assertEqual(version.patch, 0)
        self.assertEqual(version.suffix, 'dev')

    def test_bump_major(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(Version.MAJOR)

        self.assertEqual(version.major, 2)
        self.assertEqual(version.minor, 0)
        self.assertEqual(version.patch, 0)
        self.assertEqual(version.suffix, None)

    def test_bump_minor(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(Version.MINOR)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 3)
        self.assertEqual(version.patch, 0)
        self.assertEqual(version.suffix, None)

    def test_bump_patch(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(Version.PATCH)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 4)
        self.assertEqual(version.suffix, None)

    def test_bump_suffix(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(suffix='rc1')

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, 'rc1')

    def test_bump_unsuffix(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(unsuffix=True)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, None)

    def test_bump_suffix_override_unsuffix(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(suffix='rc1', unsuffix=True)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, 'rc1')

    def test_bump_no_effect(self):
        version = Version(1, 2, 3, 'dev')

        version.bump(unsuffix=False)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, 'dev')

    def test_copy(self):
        version = Version(1, 2, 3, 'dev').copy()

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, 'dev')

    def test_copy_bump(self):
        version = Version(1, 2, 3, 'dev').copy(part=Version.MINOR, unsuffix=True)

        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 3)
        self.assertEqual(version.patch, 0)
        self.assertEqual(version.suffix, None)


    def test_parse(self):
        version = Version.parse('1.2.3')

        self.assertIsNotNone(version)
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, None)

    def test_parse_with_suffix(self):
        version = Version.parse('1.2.3.rc4')

        self.assertIsNotNone(version)
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.suffix, 'rc4')
