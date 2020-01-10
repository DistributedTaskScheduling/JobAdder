"""
This module provides interfaces for Messages
"""
from abc import ABC
from ja.common.message.base import Command, Response
from ja.worker.worker_client import Worker


class WorkerCommand(Command, ABC):
    """
    Base class for all worker commands. A worker command is sent by the server
    and performed on the worker client.
    """

    def execute(self, worker_client: Worker) -> "WorkerResponse":
        """!
        Executes a WorkerCommand object on the worker and generates a
        WorkerResponse object to be sent back in return.
        @param worker_client: the Worker client that is going to be used to execute the command.
        @return: The WorkerResponse to be sent back.
        """


class WorkerResponse(Response, ABC):
    """
    Corresponding Response class for WorkerCommand.
    """
