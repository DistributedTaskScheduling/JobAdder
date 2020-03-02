"""
This command will resume a job on the work machine
"""
from typing import Dict

from ja.common.message.worker import WorkerCommand, WorkerResponse
from ja.worker.main import JobWorker


class ResumeJobCommand(WorkerCommand):

    RESPONSE_SUCCESS = "Successfully resumed job with UID %s on worker with UID %s."
    RESPONSE_NOT_PAUSED = "Could not resume job with UID %s on worker with UID %s because the job is not paused."
    RESPONSE_UNKNOWN_JOB = "Could not resume job with UID %s because worker with UID %s does not have this job."

    def __init__(self, uid: str):
        """!
        @param uid: The uid of the Job to resume on the worker client.
        """
        self._uid = uid

    @property
    def uid(self) -> str:
        """!
        @return: The uid of the Job to resume on the worker client.
        """
        return self._uid

    def execute(self, worker_client: JobWorker) -> WorkerResponse:
        """!
        Start the job on the worker machine using the provided @worker_client
        @param worker_client:  the Worker object to use for the execution
        @return: a WorkerResponse with the appropriate response
        """

    def to_dict(self) -> Dict[str, object]:
        """!
        @return: returns a dictionary that represents this object
        """
        return {"uid": self._uid}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ResumeJobCommand":
        """!
        @param property_dict A Python dictionary defining the command
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """
        uid = cls._get_str_from_dict(property_dict=property_dict, key="uid")
        cls._assert_all_properties_used(property_dict)
        return ResumeJobCommand(uid)
