import yaml
from subprocess import run, PIPE
from unittest import TestCase
from getpass import getuser
from typing import Dict

from ja.common.proxy.command_handler import CommandHandler


class CommandHandlerDummy(CommandHandler):

    def _process_command_dict(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        assert username == getuser()
        assert type_name == "COMMAND"
        command_string = str(command_dict["payload"])
        response_string = ""
        while command_string.startswith("COMMAND"):
            command_string = command_string[7:]
            response_string += "RESPONSE"
        return dict(payload=response_string)


class RemoteTest(TestCase):
    """
    Class for testing Remote and CommandHandler.
    """

    def _call_remote(self, command_string: str) -> str:
        command_dict = dict(command=dict(payload=command_string), type_name=self._command_string)
        finished_process = run(
            [
                "python3",
                "-m",
                "test.remote.remote"
            ], timeout=10, input=yaml.dump(command_dict).encode(), stdout=PIPE)
        stdout: bytes = finished_process.stdout
        response_dict = yaml.load(stdout.decode(), yaml.SafeLoader)
        return str(response_dict["payload"])

    def setUp(self) -> None:
        self._command_string = "COMMAND"
        self._response_string = "RESPONSE"
        self._long_command_string = self._command_string * 300
        self._long_response_string = self._response_string * 300
        self._command_handler_dummy = CommandHandlerDummy(socket_path="./dummy_socket")

    def test_short_command(self) -> None:
        response_string = self._call_remote(self._command_string)
        self.assertEqual(self._response_string, response_string)

    def test_long_command(self) -> None:
        response_string = self._call_remote(self._long_command_string)
        self.assertEqual(self._long_response_string, response_string)
