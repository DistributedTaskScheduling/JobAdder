from sys import stdin, stdout
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
    def __init__(self, socket_path: str):
        """!
        @param socket_path: The Unix named socket to write the Command to.
        """
        input_string = stdin.read()
        command_dict = yaml.load(input_string, Loader=yaml.SafeLoader)
        command_dict["username"] = getuser()
        command_string = yaml.dump(command_dict) + "\0"  # Null character to signal end of input.

        named_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        try:
            named_socket.connect(socket_path)
            named_socket.sendall(command_string.encode())
            response_string = ""
            while True:
                data = named_socket.recv(1024)
                if not data:  # Becomes True when socket is closed by CommandHandler.
                    break
                response_string += data.decode()
            stdout.write(response_string)
        finally:
            named_socket.close()
