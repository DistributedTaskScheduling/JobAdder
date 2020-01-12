from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase


class RegisterWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machines exists and can process jobs.
    """
    def __init__(self, work_machine_uid: str):
        """!
        @param work_machine_uid: The desired UID for this work machine.
        """

    @property
    def work_machine_uid(self) -> str:
        """!
        @return: The desired UID for this work machine.
        """

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "RegisterWorkerCommand":
        pass
