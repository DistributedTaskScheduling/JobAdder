from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase


class RetireWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machine is retiring and cannot accept further jobs.
    """
    def __init__(self, work_machine_uid: str):
        """!
        @param work_machine_uid: The UID of the work machine that is retiring.
        """

    @property
    def work_machine_uid(self) -> str:
        """!
        @return: The UID of the work machine that is retiring.
        """

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerServerCommand":
        pass
