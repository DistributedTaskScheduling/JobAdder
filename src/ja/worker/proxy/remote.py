"""
WorkerRemote is a single-class command line program.

It queues the command on the worker socket.

The commands are received on the standard input, and the worker response
will be printed on the standard output.
"""

from ja.common.proxy.remote import Remote


class WorkerRemote(Remote):
    """
    The main class of the program.
    """

    def __init__(self) -> None:
        """!
        When created the WorkerRemote starts listening to the stdin.
        """
