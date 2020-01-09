"""
This module contains classes and definitions related to handling
ServerCommands.
"""

from ja.common.proxy.command_handler import CommandHandler
from ja.server.main import JobCenter


class ServerCommandHandler(CommandHandler):
    """
    ServerCommandHandler receives ServerMessages and performs the corresponding
    actions on the server.
    """
    def __init__(self, job_center: JobCenter):
        """!
        @param job_center A reference to the singleton of the central server
        main class.
        """
