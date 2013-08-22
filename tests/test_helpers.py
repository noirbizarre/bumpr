# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from mock import patch, call

from bumpr.helpers import execute

@patch('bumpr.helpers.check_output')
@patch('subprocess.check_call')
class ExecuteTest(unittest.TestCase):
    def test_execute_quiet(self, check_call, check_output):
        execute('some command')
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
