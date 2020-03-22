from abc import ABC, abstractmethod

from ja.common.proxy.ssh import ISSHConnection, SSHConnection
from ja.common.proxy.proxy import ContinuousProxy
from ja.common.message.base import Response
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachineResources, WorkMachine, WorkMachineState
from ja.worker.message.register import RegisterWorkerCommand
from ja.worker.message.crashed import JobCrashedCommand
from ja.worker.message.done import JobDoneCommand
from ja.worker.message.retire import RetireWorkerCommand


class IWorkerServerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the central server used on the worker client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko
        """
        super().__init__(ssh_config)

    @abstractmethod
    def register_self(self, uid: str, work_machine_resources: WorkMachineResources) -> Response:
        """!
        Adds the worker client to the worker client pool of the central server.
        The server will establish an SSHConnection to the worker client and
        begin sending WorkerCommands.
        @param uid: id of the work machine.
        @param work_machine_Resources: The available resources on the work machine.
        @return: The Response from the Server.
        """

    @abstractmethod
    def unregister_self(self, uid: str) -> Response:
        """!
        Unregisters the worker client from the worker client pool of the
        central server. The server will stop dispatching new jobs to this
        machine. Once all jobs currently dispatched to this machine have
        finished, this method returns.
        @param uid: ID of the work machine.
        @return: The Response from the Server.
        """

    @abstractmethod
    def notify_job_finished(self, uid: str) -> Response:
        """!
        @param uid: uid of the job that has finished.
        @return: The Response from the Server.
        """

    @abstractmethod
    def notify_job_crashed(self, uid: str) -> Response:
        """!
        @param uid: uid of the job that has crashed.
        @return: The Response from the Server.
        """


class WorkerServerProxy(IWorkerServerProxy):
    """
    Implementation of the proxy for the central server used on the worker client.
    """

    def __init__(
            self, ssh_config: SSHConfig, remote_module: str = "ja.server.proxy.remote",
            command_string: str = "python3 -m %s"):
        self._remote_module = remote_module
        self._command_string = command_string
        super().__init__(ssh_config)

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnection(
            ssh_config=ssh_config, remote_module=self._remote_module, command_string=self._command_string)

    def register_self(self, uid: str, work_machine_resources: WorkMachineResources) -> Response:
        wm: WorkMachine = WorkMachine(uid, WorkMachineState.ONLINE, work_machine_resources)
        register_command: RegisterWorkerCommand = RegisterWorkerCommand(wm)
        response = self._ssh_connection.send_command(register_command)
        return response

    def unregister_self(self, uid: str) -> Response:
        retire_command = RetireWorkerCommand(uid)
        response = self._ssh_connection.send_command(retire_command)
        return response

    def notify_job_finished(self, uid: str) -> Response:
        done_command = JobDoneCommand(uid)
        response = self._ssh_connection.send_command(done_command)
        return response

    def notify_job_crashed(self, uid: str) -> Response:
        crashed_command = JobCrashedCommand(uid)
        response = self._ssh_connection.send_command(crashed_command)
        return response
