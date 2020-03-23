"""
This module provides the interfaces for Messages sent to the central server.
"""
from abc import ABC, abstractmethod
from typing import cast, Dict, TYPE_CHECKING

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
        ServerResponse object to be sent back in return.
        @param database: The ServerDatabase object to execute the ServerCommand
        on.
        @return: The ServerResponse to be sent back.
        """


class ServerResponse(Response, ABC):
    """
    Corresponding Response class for ServerCommand.
    """

    # TODO remove ServerResponse class if no extra functionality is implemented

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ServerResponse":
        return cast(ServerResponse, super().from_dict(property_dict))

    @classmethod
    def from_string(cls, yaml_string: str) -> "ServerResponse":
        return cast(ServerResponse, super().from_string(yaml_string))
