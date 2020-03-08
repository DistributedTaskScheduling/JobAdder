"""
This module contains classes and definitions related to handling
WorkerCommands.
"""
from typing import Dict

from ja.common.proxy.command_handler import CommandHandler
from ja.common.message.worker import WorkerCommand
from ja.common.message.worker_commands.start_job import StartJobCommand
from ja.common.message.worker_commands.pause_job import PauseJobCommand
from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from ja.common.message.base import Response
from ja.worker.docker import DockerInterface


class WorkerCommandHandler(CommandHandler):
    """
    WorkerMessageHandler receives WorkerCommand and performs the corresponding
    actions on the worker client.
    The command handler creates a socket.
    It starts listening on it for incoming commands.
    """
    def __init__(self,
                 admin_group: str, docker_interface: DockerInterface,
                 socket_path: str = "/run/jobadder-worker.socket/"):
        super().__init__(socket_path=socket_path, admin_group=admin_group)
        self._docker_interface = docker_interface

    def _process_command_dict(self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[
            str, object]:
        if not self._user_is_admin(user=username):
            return Response(
                result_string=self._INSUFFICIENT_PERM_TEMPLATE % (username, type_name), is_success=False).to_dict()
        command: WorkerCommand
        if type_name == "StartJobCommand":
            command = StartJobCommand.from_dict(command_dict)
        elif type_name == "PauseJobCommand":
            command = PauseJobCommand.from_dict(command_dict)
        elif type_name == "ResumeJobCommand":
            command = ResumeJobCommand.from_dict(command_dict)
        elif type_name == "CancelJobCommand":
            command = CancelJobCommand.from_dict(command_dict)
        else:
            return Response(result_string=self._UNKNOWN_COMMAND_TEMPLATE % type_name, is_success=False).to_dict()
        return command.execute(docker_interface=self._docker_interface).to_dict()
