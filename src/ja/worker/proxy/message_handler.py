"""
This module contains classes and definitions related to handling
WorkerCommands.
"""
from ja.common.proxy.command_handler import CommandHandler


class WorkerCommandHandler(CommandHandler):
    """
    WorkerMessageHandler receives WorkerCommand and performs the corresponding
    actions on the worker client.
    The command handler creates a socket.
    It starts listening on it for incoming commands.
    """

    def __init__(self) -> None:
        """!
        Creates the socket and listens on it.
        """
