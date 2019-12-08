"""
LocalJobAdder is a single-class command line program.

It verifies incoming user commands, checks that the user has sufficient
permissions to perform the command, and finally queues the command on the
server socket.

The commands are received on the standard input, and the server response
will be printed on the standard output.
"""


class LocalJobAdder:
    """
    The main class of the program.
    """
