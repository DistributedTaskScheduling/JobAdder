"""
This module provides the interface which all server commands implement.
"""
from ja.common.message import Message


class ServerCommand(Message):
    """
    A base class for all server commands.
    A server command is an action which is performed on the server
    and operates on the database.
    """
