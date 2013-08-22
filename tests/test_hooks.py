# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch, MagicMock

from bumpr.config import ObjectDict
from bumpr.hooks import ReadTheDocHook
from bumpr.version import Version


class ReadTheDocHookTest(unittest.TestCase):
    def setUp(self):
        self.releaser = MagicMock()
        self.releaser.version = Version.parse('1.2.3')
        self.releaser.config.__getitem__.return_value = ObjectDict({
            'id': 'fake',
            'url': 'http://{id}.somewhere.io/{tag}',
            'bump': '{version}',
            'prepare': 'latest',
        })
        self.hook = ReadTheDocHook(self.releaser)

    def test_bump(self):
        replacements = []
        self.hook.bump(replacements)
        self.assertEqual(replacements, [('http://fake.somewhere.io/latest', 'http://fake.somewhere.io/1.2.3')])

    def test_prepare(self):
        replacements = []
        self.hook.prepare(replacements)
        self.assertEqual(replacements, [('http://fake.somewhere.io/1.2.3', 'http://fake.somewhere.io/latest')])
