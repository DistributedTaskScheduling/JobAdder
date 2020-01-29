from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase
from ja.common.job import Job
from ja.common.job import JobStatus


class JobDoneCommand(WorkerServerCommand):
    """
    Informs the server that a job is done.
    """
    def __init__(self, job_uid: str):
        """!
        @param job_uid: The UID of the job that is done.
        """
        self._uid = job_uid

    @property
    def job_uid(self) -> str:
        """!
        @return: The UID of the job that is done.
        """
        return self._uid

    def execute(self, database: ServerDatabase) -> ServerResponse:
        job: Job = database.find_job_by_id(self._uid)
        job.status = JobStatus.DONE
        database.update_job(job)
        return ServerResponse(result_string="job status has been changed to done", is_success=True)

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["uid"] = self._uid
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobDoneCommand":
        _uid = str(property_dict["uid"])
        return JobDoneCommand(_uid)
