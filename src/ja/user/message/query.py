from typing import Dict

from ja.common.message.server import ServerCommand, ServerResponse
from ja.server.database.database import ServerDatabase
from ja.user.config.query import QueryCommandConfig


class QueryCommand(ServerCommand):
    """
    Command for querying the server.
    """
    def __init__(self, config: QueryCommandConfig):
        """!
        @param config: Config to create the query command from.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "QueryCommand":
        pass

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass
