from abc import ABC, abstractmethod

from ja.common.proxy.proxy import ContinuousProxy
from ja.common.proxy.ssh import SSHConfig, ISSHConnection, SSHConnection
from ja.common.message.base import Response
from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from ja.common.message.worker_commands.pause_job import PauseJobCommand
from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from ja.common.message.worker_commands.start_job import StartJobCommand
from ja.common.job import Job


class IWorkerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the worker client used on the central server.
    """

    @property
    @abstractmethod
    def uid(self) -> str:
        """!
        @return: The UID of the worker represented by this proxy.
        """

    @abstractmethod
    def dispatch_job(self, job: Job) -> Response:
        """!
        @param job: A Job to be dispatched to the worker client.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def cancel_job(self, uid: str) -> Response:
        """!
        @param uid: uid of the Job to be cancelled.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def pause_job(self, uid: str) -> Response:
        """!
        @param uid: uid of the Job to be paused.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def resume_job(self, uid: str) -> Response:
        """!
        @param uid: uid of the Job to be resumed.
        @return: The Response from the worker client.
        """


class WorkerProxyBase(IWorkerProxy, ABC):
    """
    Base class for a worker proxy class that internally uses an ISSHConnection object.
    """

    def __init__(self, uid: str, ssh_config: SSHConfig):
        """!
        @param uid: The UID of the worker represented by this proxy.
        @param ssh_config: Config for paramiko.
        """
        super().__init__(ssh_config=ssh_config)
        self._uid = uid

    @property
    def uid(self) -> str:
        return self._uid

    def dispatch_job(self, job: Job) -> Response:
        command = StartJobCommand(job)
        response = self._ssh_connection.send_command(command)
        return response

    def cancel_job(self, uid: str) -> Response:
        command = CancelJobCommand(uid)
        response = self._ssh_connection.send_command(command)
        return response

    def pause_job(self, uid: str) -> Response:
        command = PauseJobCommand(uid)
        response = self._ssh_connection.send_command(command)
        return response

    def resume_job(self, uid: str) -> Response:
        command = ResumeJobCommand(uid)
        response = self._ssh_connection.send_command(command)
        return response


class WorkerProxy(WorkerProxyBase):
    """
    Implementation of the proxy for the worker client used on the central server.
    """
    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnection(ssh_config=ssh_config,
                             remote_module="/run/jobadder-worker.socket",
                             command_string="ja-remote %s")
