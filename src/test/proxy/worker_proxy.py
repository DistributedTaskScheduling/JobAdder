from time import sleep
from getpass import getuser
from typing import List, Dict

from ja.common.job import Job
from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from ja.common.message.worker_commands.pause_job import PauseJobCommand
from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from ja.common.message.worker_commands.start_job import StartJobCommand
from ja.common.proxy.command_handler import CommandHandler
from ja.common.proxy.ssh import SSHConfig, ISSHConnection
from ja.server.proxy.proxy import WorkerProxyBase
from test.proxy.abstract import AbstractWorkerProxyTest
from test.proxy.worker_proxy_dummy import WorkerProxyDummy
from test.ssh.test_ssh_dummy import SSHConnectionDummy


class SSHDummyWorkerProxy(WorkerProxyBase):
    """
    Implementation of the proxy for the worker client that uses SSHConnectionDummy for testing.
    """

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnectionDummy(socket_path="./dummy_socket_%s" % ssh_config.hostname)


class WorkerCommandHandlerDummy(CommandHandler):

    def __init__(self, socket_path: str, jobs: List[Job]):
        super().__init__(socket_path=socket_path)
        self._worker_proxy_dummy = WorkerProxyDummy(uid=None, jobs=jobs)

    def _process_command_dict(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        assert username == getuser()
        if type_name == "StartJobCommand":
            start_command = StartJobCommand.from_dict(command_dict)
            response = self._worker_proxy_dummy.dispatch_job(start_command.job)
        elif type_name == "CancelJobCommand":
            cancel_command = CancelJobCommand.from_dict(command_dict)
            response = self._worker_proxy_dummy.cancel_job(cancel_command.uid)
        elif type_name == "PauseJobCommand":
            pause_command = PauseJobCommand.from_dict(command_dict)
            response = self._worker_proxy_dummy.pause_job(pause_command.uid)
        elif type_name == "ResumeJobCommand":
            resume_command = ResumeJobCommand.from_dict(command_dict)
            response = self._worker_proxy_dummy.resume_job(resume_command.uid)
        else:
            raise ValueError("Unknown Command type: %s" % type_name)
        return response.to_dict()


class WorkerProxyTest(AbstractWorkerProxyTest):
    def setUp(self) -> None:
        super().setUp()
        ssh_config_empty = SSHConfig(hostname="empty")
        self._empty_worker = SSHDummyWorkerProxy(uid="empty-worker", ssh_config=ssh_config_empty)
        self._command_handler_empty = WorkerCommandHandlerDummy(socket_path="./dummy_socket_empty", jobs=[])
        ssh_config_busy = SSHConfig(hostname="busy")
        self._busy_worker = SSHDummyWorkerProxy(uid="busy-worker", ssh_config=ssh_config_busy)
        self._command_handler_empty = WorkerCommandHandlerDummy(
            socket_path="./dummy_socket_busy", jobs=[self._job_1, self._job_2])
        sleep(0.01)  # Wait until the command handler has created the socket.
