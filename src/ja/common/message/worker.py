"""
This module provides interfaces for Messages
"""
from abc import ABC
from ja.common.message.base import Command, Response


class WorkerCommand(Command, ABC):
    """
    Base class for all worker commands. A worker command is sent by the server
    and performed on the worker client.
    """

    # TODO define target for worker client
    def execute(self, target: object) -> "WorkerResponse":
        """!
        Executes a WorkerCommand object on the worker and generates a
        WorkerResponse object to be sent back in return.
        @param target:
        @return: The WorkerResponse to be sent back.
        """


class WorkerResponse(Response, ABC):
    """
    Corresponding Response class for WorkerCommand.
    """
