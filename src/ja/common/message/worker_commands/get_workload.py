"""
This command will get the cpu_load and other information about the state of the work machine
"""
from typing import Dict

from ja.common.message.worker import WorkerCommand, WorkerResponse
from ja.worker.docker import DockerInterface


class GetWorkloadCommand(WorkerCommand):

    def execute(self, docker_interface: DockerInterface) -> WorkerResponse:
        """!
        Get the information about the work machine using the provided @worker_client
        @param docker_interface: the docker interface to use for the execution.
        @return: a WorkerResponse with the appropriate response
        """

    def to_dict(self) -> Dict[str, object]:
        """!
        @return: returns a dictionary that represents this object
        """

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "GetWorkloadCommand":
        """!
        @param property_dict A Python dictionary defining the command
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """
