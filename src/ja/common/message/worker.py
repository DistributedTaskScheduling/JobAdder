"""
This module provides interfaces for Messages
"""
from abc import ABC
from typing import Dict, cast

from ja.common.message.base import Command, Response
from ja.worker.main import JobWorker


class WorkerCommand(Command, ABC):
    """
    Base class for all worker commands. A worker command is sent by the server
    and performed on the worker client.
    """

    def execute(self, worker_client: JobWorker) -> "WorkerResponse":
        """!
        Executes a WorkerCommand object on the worker and generates a
        WorkerResponse object to be sent back in return.
        @param worker_client: the Worker client that is going to be used to execute the command.
        @return: The WorkerResponse to be sent back.
        """


class WorkerResponse(Response):
    """
    Corresponding Response class for WorkerCommand.
    """

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerResponse":
        return cast(WorkerResponse, super().from_dict(property_dict))

    @classmethod
    def from_string(cls, yaml_string: str) -> "WorkerResponse":
        return cast(WorkerResponse, super().from_string(yaml_string))
