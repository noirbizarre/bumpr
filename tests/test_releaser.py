# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from bumpr.config import Config
from bumpr.releaser import Releaser
from bumpr.version import Version


class ReleaserTest(unittest.TestCase):
    def test_constructor(self):
        config = Config({
            'module': 'bumpr'
        })
        releaser = Releaser(config)

        self.assertEqual(releaser.module.__name__, 'bumpr')
        self.assertIsNotNone(releaser.module_file)
        self.assertIsInstance(releaser.prev_version, Version)
        self.assertIsInstance(releaser.version, Version)
        self.assertIsInstance(releaser.next_version, Version)

        self.assertIsNone(releaser.timestamp)

        self.assertFalse(hasattr(releaser, 'vcs'))
        self.assertFalse(hasattr(releaser, 'diffs'))

        self.assertEqual(releaser.modified, set())
        self.assertEqual(releaser.hooks, [])
