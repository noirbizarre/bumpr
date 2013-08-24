#!/usr/bin/env python
from __future__ import print_function, unicode_literals

from bumpr import log
log.declare()  # Fix tests with custom log level

import os
import sys
try:
    import unittest2 as unittest
except:
    import unittest


def run_tests():
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    runner = unittest.runner.TextTestRunner()
    runner.run(tests)


if __name__ == '__main__':
    run_tests()
