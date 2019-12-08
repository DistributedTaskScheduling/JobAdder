"""
This module provides the interfaces for Messages passed between the user client
and the central server.
"""
from ja.common.message.base import Command, Response


class ServerCommand(Command):
    """
    A base class for all server commands. A server command is an action which
    is sent by the user client and performed on the server. ServerCommands
    typically operate on the server database.
    """


class ServerResponse(Response):
    """
    A base class for all server responses. A server response is a Response
    retrieved by the user client from the central server.
    """
