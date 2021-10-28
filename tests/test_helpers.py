from subprocess import CalledProcessError

import pytest

from bumpr.helpers import BumprError, check_output, execute


@pytest.fixture
def check_call(mocker):
    yield mocker.patch("subprocess.check_call")


@pytest.fixture(name="check_output")
def check_output_mock(mocker):
    yield mocker.patch("bumpr.helpers.check_output")


class ExecuteTest(object):
    def test_execute_quiet(self, check_call, check_output):
        output = "some output"
        check_output.return_value = output
        assert execute("some command") == output
        check_output.assert_called_with(["some", "command"])
        assert not check_call.called

    def test_execute_verbose(self, check_call, check_output):
        execute("some command", verbose=True)
        check_call.assert_called_with(["some", "command"])
        assert not check_output.called

    def test_execute_array(self, check_call, check_output):
        execute(["some", "command"])
        check_output.assert_called_with(["some", "command"])
        assert not check_call.called

    def test_execute_quoted(self, check_output):
        execute('some command "with quote"')
        check_output.assert_called_with(["some", "command", "with quote"])

    def test_execute_format(self, check_output):
        execute("some command {key}", replacements={"key": "value"})
        check_output.assert_called_with(["some", "command", "value"])

    def test_execute_format_array(self, check_output):
        execute(["some", "command", "{key}"], replacements={"key": "value"})
        check_output.assert_called_with(["some", "command", "value"])

    def test_execute_dry(self, check_call, check_output):
        execute("some command", dryrun=True)
        assert not check_call.called
        assert not check_output.called

    def test_execute_multiple(self, check_output, mocker):
        execute(
            """
            some command
            another command
        """
        )

        expected = (
            mocker.call(["some", "command"]),
            mocker.call(["another", "command"]),
        )
        for executed, expected in zip(check_output.call_args_list, expected):
            assert executed == expected

    def test_execute_multiple_array(self, check_output, mocker):
        execute(
            (
                ["some", "command"],
                ["another", "command"],
            )
        )

        expected = (
            mocker.call(["some", "command"]),
            mocker.call(["another", "command"]),
        )
        for executed, expected in zip(check_output.call_args_list, expected):
            assert executed == expected

    def test_execute_error_quiet(self, check_output, mocker):
        error = CalledProcessError(1, "cmd")
        error.output = "some output"
        check_output.side_effect = error

        with pytest.raises(BumprError):
            mocker.patch("builtins.print")
            execute("some failed command")

    def test_execute_error_verbose(self, check_call):
        check_call.side_effect = CalledProcessError(1, "cmd")

        with pytest.raises(BumprError):
            execute("some failed command", verbose=True)


def test_check_output():
    assert check_output(["echo", "123"]).strip() == "123"
