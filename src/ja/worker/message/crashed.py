from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase


class JobCrashedCommand(WorkerServerCommand):
    """
    Informs the server that a job has crashed.
    """
    def __init__(self, job_uid: str):
        """!
        @param job_uid: The UID of the job that has crashed.
        """

    @property
    def job_uid(self) -> str:
        """!
        @return: The UID of the job that has crashed.
        """

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobCrashedCommand":
        pass
