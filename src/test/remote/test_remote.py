import yaml
from subprocess import run, PIPE
from unittest import TestCase
from getpass import getuser

from ja.common.proxy.command_handler import CommandHandler


class CommandHandlerDummy(CommandHandler):

    def _process_command_string(self, command_string: str, username: str) -> str:
        print("LAMO")
        assert username == getuser()
        response_string = ""
        while command_string.startswith("COMMAND"):
            command_string = command_string[7:]
            response_string += "RESPONSE"
        return response_string


class RemoteTest(TestCase):
    """
    Class for testing Remote and CommandHandler.
    IMPORTANT: THESE TESTS WILL FAIL IF YOU DON'T RUN THEM FROM THE BASE SRC DIRECTORY.
    """

    @staticmethod
    def _call_remote(command_string: str) -> str:
        command_dict = dict(command=command_string)
        finished_process = run(
            [
                "python3",
                "test/remote/remote"  # Change to "remote" to run from current directory
            ], timeout=10, input=yaml.dump(command_dict).encode(), stdout=PIPE)
        stdout: bytes = finished_process.stdout
        return stdout.decode()

    def setUp(self) -> None:
        self._command_string = "COMMAND"
        self._response_string = "RESPONSE"
        self._long_command_string = self._command_string * 300
        self._long_response_string = self._response_string * 300
        self._command_handler_dummy = CommandHandlerDummy(socket_path="./dummy_socket")

    def test_short_command(self) -> None:
        response_string = RemoteTest._call_remote(self._command_string)
        self.assertEqual(self._response_string, response_string)

    def test_long_command(self) -> None:
        response_string = RemoteTest._call_remote(self._long_command_string)
        self.assertEqual(self._long_response_string, response_string)
