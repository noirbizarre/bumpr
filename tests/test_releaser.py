# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch

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

    def test_test(self):
        config = Config({
            'module': 'bumpr',
            'tests': 'test command',
        })
        releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.test()
            mock.assert_called_with('test command')

    def test_publish(self):
        config = Config({
            'module': 'bumpr',
            'publish': 'publish command',
        })
        releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.publish()
            mock.assert_called_with('publish command')

    def test_clean(self):
        config = Config({
            'module': 'bumpr',
            'clean': 'clean command',
        })
        releaser = Releaser(config)

        with patch.object(releaser, 'execute') as mock:
            releaser.clean()
            mock.assert_called_with('clean command')
