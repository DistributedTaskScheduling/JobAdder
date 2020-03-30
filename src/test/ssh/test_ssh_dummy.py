from io import StringIO
from typing import Dict
from unittest import TestCase
from time import sleep
import yaml
from getpass import getuser

from ja.common.message.base import Response, Command
from ja.common.message.server import ServerCommand
from ja.common.proxy.ssh import ISSHConnection
from ja.common.proxy.remote import Remote
from test.proxy.threaded_command_handler import ThreadedCommandHandler
from ja.server.database.database import ServerDatabase


class SSHConnectionDummy(ISSHConnection):
    """
    Dummy class for SSHConnection. Directly creates a Remote object on the local machine.
    """
    def __init__(self, socket_path: str):
        self._socket_path = socket_path

    def send_command(self, command: Command) -> Response:
        command_dict = dict(command=command.to_dict(), type_name=command.__class__.__name__)
        input_stream = StringIO(initial_value=yaml.dump(command_dict))
        output_stream = StringIO()
        Remote(socket_path=self._socket_path, input_stream=input_stream, output_stream=output_stream)
        output_stream.seek(0)
        response_dict = yaml.load(output_stream.read(), yaml.SafeLoader)
        return Response.from_dict(response_dict)

    def close(self) -> None:
        pass

    def send_dummy_command(self) -> None:
        pass


class ServerCommandDummy(ServerCommand):
    def __init__(self, payload: str):
        self._payload = payload

    def execute(self, database: ServerDatabase) -> "Response":
        return Response(result_string=self._payload * 2, is_success=True)

    def to_dict(self) -> Dict[str, object]:
        return {"payload": self._payload}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ServerCommandDummy":
        return cls(cls._get_str_from_dict(property_dict=property_dict, key="payload"))


class CommandHandlerDummy(ThreadedCommandHandler):
    def _process_command_dict(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        assert username == getuser()
        assert type_name == "ServerCommandDummy"
        command = ServerCommandDummy.from_dict(command_dict)
        response = command.execute(database=None)
        return response.to_dict()


class SSHConnectionDummyTest(TestCase):
    """
    Class for testing SSHConnectionDummy
    """
    def setUp(self) -> None:
        socket_path = "./dummy_socket"
        self._payload = "PAYLOAD"
        self._server_command = ServerCommandDummy(self._payload)
        self._command_handler = CommandHandlerDummy(socket_path=socket_path)
        sleep(0.01)  # Wait until the command handler has created the socket.
        self._ssh_connection_dummy = SSHConnectionDummy(socket_path=socket_path)

    def test_send_command(self) -> None:
        response = self._ssh_connection_dummy.send_command(self._server_command)
        self.assertTrue(response.is_success)
        self.assertEqual(response.result_string, self._payload * 2)
