from abc import ABC, abstractmethod

from ja.common.proxy.proxy import ContinuousProxy
from ja.common.message.server import ServerResponse
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachineResources
from ja.worker.message.register import RegisterWorkerCommand
from ja.worker.message.retire import RetireWorkerCommand
from ja.worker.message.done import JobDoneCommand
from ja.worker.message.crashed import JobCrashedCommand
from ja.server.database.database import ServerDatabase


class IWorkerServerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the central server used on the worker client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko
        """

    @abstractmethod
    def register_self(self, work_machine_resources: WorkMachineResources) -> ServerResponse:
        """!
        Adds the worker client to the worker client pool of the central server.
        The server will establish an SSHConnection to the worker client and
        begin sending WorkerCommands.
        @param work_machine_resources: The resources available on this work machine.
        @return: The Response from the Server.
        """

    @abstractmethod
    def unregister_self(self) -> ServerResponse:
        """!
        Unregisters the worker client from the worker client pool of the
        central server. The server will stop dispatching new jobs to this
        machine. Once all jobs currently dispatched to this machine have
        finished, this method returns.
        @return: The Response from the Server.
        """

    @abstractmethod
    def notify_job_finished(self, uid: str) -> ServerResponse:
        """!
        @param uid: uid of the job that has finished.
        @return: The Response from the Server.
        """

    @abstractmethod
    def notify_job_crashed(self, uid: str) -> ServerResponse:
        """!
        @param uid: uid of the job that has crashed.
        @return: The Response from the Server.
        """


class WorkerServerProxy(IWorkerServerProxy):
    """
    Implementation of the proxy for the central server used on the worker client.
    """

    def __init__(self, ssh_config: SSHConfig, uid: str, database: ServerDatabase):
        self._ssh_config = ssh_config
        self._uid = uid
        self._database = database

    def register_self(self, work_machine_resources: WorkMachineResources) -> ServerResponse:
        register_command = RegisterWorkerCommand(self._uid)
        response = register_command.execute(database=self._database, resources=work_machine_resources)
        return response

    def unregister_self(self) -> ServerResponse:
        retire_command = RetireWorkerCommand(self._uid)
        response = retire_command.execute(database=self._database, resources=None)
        return response

    def notify_job_finished(self, uid: str) -> ServerResponse:
        job_done_command = JobDoneCommand(self._uid)
        response = job_done_command.execute(database=self._database, resources=None)
        return response

    def notify_job_crashed(self, uid: str) -> ServerResponse:
        job_crashed_command = JobCrashedCommand(self._uid)
        response = job_crashed_command.execute(database=self._database, resources=None)
        return response
