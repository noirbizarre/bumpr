# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from nose.plugins import Plugin

from bumpr.log import declare


class DryRunLoggerPlugin(Plugin):
    name = 'dryrun-logger'
    enabled = True

    def configure(self, options, conf):
        pass  # always on

    def begin(self):
        declare()  # Fix tests with custom log level
