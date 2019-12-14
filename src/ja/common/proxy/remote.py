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
    def __init__(self, socket: str):
        """!
        @param socket: The Unix named socket to write the Command to.
        """
