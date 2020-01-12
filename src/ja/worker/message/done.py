from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase


class JobDoneCommand(WorkerServerCommand):
    """
    Informs the server that a job is done.
    """
    def __init__(self, job_uid: str):
        """!
        @param job_uid: The UID of the job that is done.
        """

    @property
    def job_uid(self) -> str:
        """!
        @return: The UID of the job that is done.
        """

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobDoneCommand":
        pass
