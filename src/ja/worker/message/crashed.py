from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase
from ja.common.job import Job
from ja.common.job import JobStatus


class JobCrashedCommand(WorkerServerCommand):
    """
    Informs the server that a job has crashed.
    """
    def __init__(self, job_uid: str):
        """!
        @param job_uid: The UID of the job that has crashed.
        """
        self._uid = job_uid

    @property
    def job_uid(self) -> str:
        """!
        @return: The UID of the job that has crashed.
        """
        return self._uid

    def execute(self, database: ServerDatabase) -> ServerResponse:
        job: Job = database.find_job_by_id(self._uid)
        job.status = JobStatus.CRASHED
        database.update_job(job)
        return ServerResponse(result_string="job status has been changed to crashed", is_success=True)

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["uid"] = self._uid
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobCrashedCommand":
        uid = str(property_dict["uid"])
        return JobCrashedCommand(uid)
