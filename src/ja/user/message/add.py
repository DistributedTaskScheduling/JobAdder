from typing import Dict

from ja.common.message.server import ServerCommand, ServerResponse
from ja.server.database.database import ServerDatabase
from ja.user.config.add import AddCommandConfig


class AddCommand(ServerCommand):
    """
    Command for adding a job.
    """
    def __init__(self, config: AddCommandConfig):
        """!
        @param config: Config to create the add command from.
        """
        self._config = config

    @property
    def config(self) -> AddCommandConfig:
        """!
        @return the AddCommandConfig for this Command.
        """
        return self._config

    def to_dict(self) -> Dict[str, object]:
        return self._config.to_dict()

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "AddCommand":
        return AddCommand(AddCommandConfig.from_dict(property_dict))

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass
