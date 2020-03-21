"""
This module provides interfaces for Messages
"""
from abc import ABC
from typing import Dict, cast, TYPE_CHECKING

from ja.common.message.base import Command, Response
if TYPE_CHECKING:
    from ja.worker.docker import DockerInterface


class WorkerCommand(Command, ABC):
    """
    Base class for all worker commands. A worker command is sent by the server
    and performed on the worker client.
    """

    def execute(self, docker_interface: "DockerInterface") -> Response:
        """!
        Executes a WorkerCommand object on the worker and generates a
        WorkerResponse object to be sent back in return.
        @param docker_interface: the docker interface to use for the execution.
        @return: The WorkerResponse to be sent back.
        """


class WorkerResponse(Response):
    """
    Corresponding Response class for WorkerCommand.
    """

    # TODO remove WorkerResponse class if no extra functionality is implemented

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerResponse":
        return cast(WorkerResponse, super().from_dict(property_dict))

    @classmethod
    def from_string(cls, yaml_string: str) -> "WorkerResponse":
        return cast(WorkerResponse, super().from_string(yaml_string))
