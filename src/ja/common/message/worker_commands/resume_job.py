"""
This command will resume a job on the work machine
"""
from typing import Dict
from docker.errors import APIError  # type: ignore

from ja.common.message.worker import WorkerCommand
from ja.common.message.base import Response
from ja.worker.docker import DockerInterface


class ResumeJobCommand(WorkerCommand):

    RESPONSE_SUCCESS = "Successfully resumed job with UID %s on worker with UID %s."
    RESPONSE_NOT_PAUSED = "Could not resume job with UID %s on worker with UID %s because the job is not paused."
    RESPONSE_UNKNOWN_JOB = "Could not resume job with UID %s because worker with UID %s does not have this job."

    def __init__(self, uid: str):
        """!
        @param uid: The uid of the Job to resume on the worker client.
        """
        self._uid = uid

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ResumeJobCommand) and self.uid == other.uid

    @property
    def uid(self) -> str:
        """!
        @return: The uid of the Job to resume on the worker client.
        """
        return self._uid

    def execute(self, docker_interface: DockerInterface) -> Response:
        """!
        Start the job on the worker machine using the provided @worker_client
        @param docker_interface: the docker interface to use for the execution.
        @return: a WorkerResponse with the appropriate response
        """
        try:
            docker_interface.resume_job(uid=self.uid)
            return Response(self.RESPONSE_SUCCESS % (self.uid, docker_interface.worker_uid), is_success=True)
        except KeyError:
            return Response(self.RESPONSE_UNKNOWN_JOB % (self.uid, docker_interface.worker_uid), is_success=False)
        except APIError:
            return Response(self.RESPONSE_NOT_PAUSED % (self.uid, docker_interface.worker_uid), is_success=False)

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
