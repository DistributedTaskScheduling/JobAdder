import os
import socket
from abc import ABC, abstractmethod
from threading import Thread
import yaml


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
    def __init__(self, socket_path: str):
        """!
        @param socket_path: The Unix named socket to listen for Commands on.
        """
        self._socket_path = socket_path
        self._listen_thread = Thread(target=self._listen)
        self._listen_thread.daemon = True  # Ensures that the thread is killed when main thread exits
        self._listen_thread.start()

    def _listen(self) -> None:
        # Make sure the socket does not already exist
        try:
            os.unlink(self._socket_path)
        except OSError:
            if os.path.exists(self._socket_path):
                raise
        named_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        named_socket.bind(self._socket_path)
        named_socket.listen(1)

        while True:
            connection, client_address = named_socket.accept()
            try:
                input_string = ""
                while True:
                    data = connection.recv(1024)
                    if data[-1:] == b"\0":
                        input_string += data[:-1].decode()
                        break
                    input_string += data.decode()
                input_dict = yaml.load(input_string, yaml.SafeLoader)
                response_string = self._process_command_string(input_dict["command"], input_dict["username"])
                connection.sendall(response_string.encode())
            finally:
                connection.close()

    @abstractmethod
    def _process_command_string(self, command_string: str, username: str) -> str:
        pass
