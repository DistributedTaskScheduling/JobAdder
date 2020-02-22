from sys import stdin, stdout
from typing import TextIO
from getpass import getuser
import yaml
import socket


class Remote(object):
    """
    Class for remote objects accessed by Proxy objects.
    Remotes are single-class command line programs.

    Receives a Command object represented by a YAML string on stdin. Asserts
    that the user specified in the YAML document is the user calling the
    Remote. Passes on the YAML string to a CommandHandler object via a socket.
    Listens for a Response (as YAML string) on the same socket. Writes the
    Response YAML string to stdout.
    """
    def __init__(self, socket_path: str, input_stream: TextIO = stdin, output_stream: TextIO = stdout):
        """!
        @param socket_path: The Unix named socket to write the Command to.
        @param output_stream: The output stream to write the Response to.
        """
        input_string = input_stream.read()
        command_dict = yaml.load(input_string, Loader=yaml.SafeLoader)
        command_dict["username"] = getuser()
        command_string = yaml.dump(command_dict)

        named_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        try:
            named_socket.connect(socket_path)
            command_string_bytes = command_string.encode()
            # First 8 bytes encode command length:
            named_socket.sendall(len(command_string_bytes).to_bytes(length=8, byteorder="big"))
            named_socket.sendall(command_string_bytes)
            response_string = ""
            while True:
                data = named_socket.recv(1024)
                if not data:  # Becomes True when socket is closed by CommandHandler.
                    break
                response_string += data.decode()
            output_stream.write(response_string)
            output_stream.write(response_string)
        finally:
            named_socket.close()
