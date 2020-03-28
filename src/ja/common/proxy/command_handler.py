import os
import socket
from abc import ABC, abstractmethod
from ja.common.message.base import Response
import yaml
from typing import Dict
import grp
import logging

logger = logging.getLogger(__name__)


class CommandHandler(ABC):
    """
    Abstract base class that handles Commands received by Remote objects.
    Commands are transferred from Remote to MessageHandler by socket as YAML
    string. Once initialized, continuously listens for Commands.
    When a Command is received it is validated syntactically first: the
    CommandHandler tries to construct a Command of the correct type from the
    YAML string.
    Afterwards the Command is validated semantically: the CommandHandler checks
    if the user has the necessary permissions to perform the Command, if any
    specified objects actually exist, etc.
    If both validations pass, the Command is executed.
    Always prints back a Response as YAML string to the socket at the end. The
    success property of the Response is True if both validations were passed
    and the Command was executed without error, and is false otherwise.
    """
    def __init__(self, socket_path: str, admin_group: str = "jobadder"):
        """!
        @param socket_path: The Unix named socket to listen for Commands on.
        @param admin_group The name of the administrator group.
        """
        self._socket_path = socket_path
        self._running = True
        self._admin_group = admin_group

        # Make sure the socket does not already exist
        try:
            os.unlink(self._socket_path)
        except OSError:
            if os.path.exists(self._socket_path):
                raise
        self._named_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        self._named_socket.bind(self._socket_path)
        self._named_socket.listen(1)

    _INSUFFICIENT_PERM_TEMPLATE = "User %s has insufficient permissions for the requested action %s."
    _UNKNOWN_COMMAND_TEMPLATE = "Unknown command: %s."

    @abstractmethod
    def _process_command_dict(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        pass

    def _check_exit_or_process_command(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        if type_name == "KillCommand":
            if self._user_is_admin(username):
                self._running = False
                return Response("Shutting down ...", True).to_dict()
            else:
                return Response("Insufficient permissions to shut down JobAdder daemon.", False).to_dict()
        return self._process_command_dict(command_dict, type_name, username)

    def _user_is_admin(self, user: str) -> bool:
        groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
        return self._admin_group in groups or user == self._admin_group

    def main_loop(self) -> None:
        """!
        Run the main loop of a JobAdder daemon (server or worker).
        """
        while self._running:
            connection, client_address = self._named_socket.accept()
            try:
                command_bytes = bytes(0)  # First 8 bytes encode command length
                command_length = None
                while command_length is None or len(command_bytes) < command_length:
                    command_bytes += connection.recv(1024)
                    if command_length is None and len(command_bytes) >= 8:
                        command_length = int.from_bytes(bytes=command_bytes[:8], byteorder="big")
                        command_bytes = command_bytes[8:]

                input_string = command_bytes.decode()

                input_dict = yaml.load(input_string, yaml.SafeLoader)
                response_dict = self._check_exit_or_process_command(
                    command_dict=input_dict["command"],
                    type_name=input_dict["type_name"],
                    username=input_dict["username"]
                )
                logger.info("handling %s command" % input_dict["type_name"])
                logger.debug(input_dict["command"])
                response_string = yaml.dump(response_dict)
                connection.sendall(response_string.encode())
            finally:
                connection.close()
