"""
This command will pause a running job on the work machine
"""
from typing import Dict

from ja.common.message.worker import WorkerCommand, WorkerResponse
from ja.worker.main import JobWorker


class PauseJobCommand(WorkerCommand):

    def execute(self, worker_client: JobWorker) -> WorkerResponse:
        """!
        Pause the job on the worker machine using the provided @worker_client
        @param worker_client:  the Worker object to use for the execution
        @return: a WorkerResponse with the appropriate response
        """

    def to_dict(self) -> Dict[str, object]:
        """!
        @return: returns a dictionary that represents this object
        """

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "PauseJobCommand":
        """!
        @param property_dict A Python dictionary defining the command
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """
