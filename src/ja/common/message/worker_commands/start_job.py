"""
This command will start a new job on the work machine
"""
from typing import Dict

from ja.common.job import Job
from ja.common.message.worker import WorkerCommand
from ja.common.message.base import Response
from ja.worker.docker import DockerInterface


class StartJobCommand(WorkerCommand):

    RESPONSE_SUCCESS = "Successfully dispatched job with UID %s to worker with UID %s."
    RESPONSE_DUPLICATE = "Could not dispatch job with UID %s because worker with UID %s already has this job."

    def __init__(self, job: Job):
        """!
        @param job: The Job to start on the worker client.
        """
        self._job = job

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StartJobCommand) and self.job == other.job

    @property
    def job(self) -> Job:
        """!
        @return: The Job to start on the worker client.
        """
        return self._job

    def execute(self, docker_interface: DockerInterface) -> Response:
        """!
        Start the job on the worker machine using the provided @worker_client
        @param docker_interface: the docker interface to use for the execution.
        @return: a WorkerResponse with the appropriate response
        """
        try:
            docker_interface.add_job(job=self.job)
            return Response(self.RESPONSE_SUCCESS % (self.job.uid, docker_interface.worker_uid), is_success=True)
        except ValueError:
            return Response(self.RESPONSE_DUPLICATE % (self.job.uid, docker_interface.worker_uid), is_success=False)

    def to_dict(self) -> Dict[str, object]:
        """!
        @return: returns a dictionary that represents this object
        """
        return {"job": self._job.to_dict()}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "StartJobCommand":
        """!
        @param property_dict A Python dictionary defining the command
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """
        job = Job.from_dict(cls._get_dict_from_dict(property_dict=property_dict, key="job"))
        cls._assert_all_properties_used(property_dict)
        return StartJobCommand(job)
