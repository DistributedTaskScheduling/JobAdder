"""
This module provides interfaces for Messages
"""
from abc import ABC
from typing import TYPE_CHECKING

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
        Response object to be sent back in return.
        @param docker_interface: the docker interface to use for the execution.
        @return: The Response to be sent back.
        """
