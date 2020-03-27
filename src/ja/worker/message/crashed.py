from typing import Dict

from ja.common.job import JobStatus
from ja.worker.message.base import WorkerServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase


class JobCrashedCommand(WorkerServerCommand):
    """
    Informs the server that a job has crashed.
    """

    def __init__(self, job_uid: str):
        """!
        @param job_uid: The UID of the job that has crashed.
        """
        self._job_uid = job_uid

    @property
    def job_uid(self) -> str:
        """!
        @return: The UID of the job that has crashed.
        """
        return self._job_uid

    def execute(self, database: ServerDatabase) -> Response:
        job_entry = database.find_job_by_id(self._job_uid)
        if job_entry is None:
            raise ValueError("There is no job with %s id on the server" % self._job_uid)
        self._free_resources_for_job(database, job_entry, JobStatus.CRASHED)
        return Response("Job with uid: {} crashed!".format(self._job_uid), True)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, JobCrashedCommand):
            return self._job_uid == o._job_uid
        return False

    def to_dict(self) -> Dict[str, object]:
        n_dict: Dict[str, object] = dict()
        n_dict["uid"] = self._job_uid
        return n_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobCrashedCommand":
        uid = cls._get_str_from_dict(property_dict, key="uid", mandatory=True)
        cls._assert_all_properties_used(property_dict)
        return JobCrashedCommand(uid)
