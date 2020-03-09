"""
This command will pause a running job on the work machine
"""
from typing import Dict
from docker.errors import APIError  # type: ignore

from ja.common.message.worker import WorkerCommand
from ja.common.message.base import Response
from ja.worker.docker import DockerInterface


class PauseJobCommand(WorkerCommand):

    RESPONSE_SUCCESS = "Successfully paused job with UID %s on worker with UID %s."
    RESPONSE_NOT_RUNNING = "Could not pause job with UID %s on worker with UID %s because the job is not running."
    RESPONSE_UNKNOWN_JOB = "Could not pause job with UID %s because worker with UID %s does not have this job."

    def __init__(self, uid: str):
        """!
        @param uid: The uid of the Job to pause on the worker client.
        """
        self._uid = uid

    @property
    def uid(self) -> str:
        """!
        @return: The uid of the Job to pause on the worker client.
        """
        return self._uid

    def execute(self, docker_interface: DockerInterface) -> Response:
        """!
        Pause the job on the worker machine using the provided @worker_client
        @param docker_interface: the docker interface to use for the execution.
        @return: a WorkerResponse with the appropriate response
        """
        try:
            docker_interface.pause_job(uid=self.uid)
            return Response(self.RESPONSE_SUCCESS % (self.uid, docker_interface.worker_uid), is_success=True)
        except KeyError:
            return Response(self.RESPONSE_UNKNOWN_JOB % (self.uid, docker_interface.worker_uid), is_success=False)
        except APIError:
            return Response(self.RESPONSE_NOT_RUNNING % (self.uid, docker_interface.worker_uid), is_success=False)

    def to_dict(self) -> Dict[str, object]:
        """!
        @return: returns a dictionary that represents this object
        """
        return {"uid": self._uid}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "PauseJobCommand":
        """!
        @param property_dict A Python dictionary defining the command
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """
        uid = cls._get_str_from_dict(property_dict=property_dict, key="uid")
        cls._assert_all_properties_used(property_dict)
        return PauseJobCommand(uid)
