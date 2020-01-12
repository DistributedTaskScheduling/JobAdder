from typing import Dict

from ja.common.message.server import ServerCommand, ServerResponse
from ja.server.database.database import ServerDatabase
from ja.user.config.cancel import CancelCommandConfig


class CancelCommand(ServerCommand):
    """
    Command for canceling a job.
    """
    def __init__(self, config: CancelCommandConfig):
        """!
        @param config: Config to create the cancel command from.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "CancelCommand":
        pass

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass
