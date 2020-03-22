"""
This module provides the interfaces for Messages sent to the central server.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ja.common.message.base import Command, Response
if TYPE_CHECKING:
    from ja.server.database.database import ServerDatabase


class ServerCommand(Command, ABC):
    """
    Base class for all server commands. A server command is an action which is
    sent by a user client or the worker client and performed on the server.
    ServerCommands typically operate on the server database.
    """

    @abstractmethod
    def execute(self, database: "ServerDatabase") -> Response:
        """!
        Executes a ServerCommand object on the server and generates a
        Response object to be sent back in return.
        @param database: The ServerDatabase object to execute the ServerCommand
        on.
        @return: The Response to be sent back.
        """
