# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch, call
from subprocess import CalledProcessError

from bumpr.helpers import execute, BumprError

IS_PY3 = sys.version_info[0] == 3


@patch('bumpr.helpers.check_output')
@patch('subprocess.check_call')
class ExecuteTest(unittest.TestCase):
    def test_execute_quiet(self, check_call, check_output):
        output = 'some output'
        check_output.return_value = output
        self.assertEqual(execute('some command'), output)
        check_output.assert_called_with(['some', 'command'])
        self.assertFalse(check_call.called)

    def test_execute_verbose(self, check_call, check_output):
        execute('some command', verbose=True)
        check_call.assert_called_with(['some', 'command'])
        self.assertFalse(check_output.called)

    def test_execute_array(self, check_call, check_output):
        execute(['some', 'command'])
        check_output.assert_called_with(['some', 'command'])
        self.assertFalse(check_call.called)

    def test_execute_quoted(self, check_call, check_output):
        execute('some command "with quote"')
        check_output.assert_called_with(['some', 'command', 'with quote'])

    def test_execute_format(self, check_call, check_output):
        execute('some command {key}', replacements={'key': 'value'})
        check_output.assert_called_with(['some', 'command', 'value'])

    def test_execute_format_array(self, check_call, check_output):
        execute(['some', 'command', '{key}'], replacements={'key': 'value'})
        check_output.assert_called_with(['some', 'command', 'value'])

    def test_execute_dry(self, check_call, check_output):
        execute('some command', dryrun=True)
        self.assertFalse(check_call.called)
        self.assertFalse(check_output.called)

    def test_execute_multiple(self, check_call, check_output):
        execute('''
            some command
            another command
        ''')

        expected = (
            call(['some', 'command']),
            call(['another', 'command']),
        )
        self.assertSequenceEqual(check_output.call_args_list, expected)

    def test_execute_multiple_array(self, check_call, check_output):
        execute((
            ['some', 'command'],
            ['another', 'command'],
        ))

        expected = (
            call(['some', 'command']),
            call(['another', 'command']),
        )
        self.assertSequenceEqual(check_output.call_args_list, expected)

    def test_execute_error_quiet(self, check_call, check_output):
        error = CalledProcessError(1, 'cmd')
        error.output = 'some output'
        check_output.side_effect = error

        with self.assertRaises(BumprError):
            to_patch = '{0}.print'.format('builtins' if IS_PY3 else '__builtin__')
            with patch(to_patch):
                execute('some failed command')

    def test_execute_error_verbose(self, check_call, check_output):
        check_call.side_effect = CalledProcessError(1, 'cmd')

        with self.assertRaises(BumprError):
            execute('some failed command', verbose=True)
