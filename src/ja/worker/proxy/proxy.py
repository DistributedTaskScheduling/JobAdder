from abc import ABC, abstractmethod

from ja.common.proxy.proxy import ContinuousProxy
from ja.common.message.server import ServerResponse
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachineResources


class IWorkerServerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the central server used on the worker client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko
        """

    @abstractmethod
    def register_self(self, uid: str, work_machine_resources: WorkMachineResources) -> ServerResponse:
        """!
        Adds the worker client to the worker client pool of the central server.
        The server will establish an SSHConnection to the worker client and
        begin sending WorkerCommands.
        @param uid: id of the work machine.
        @param work_machine_Resources: The available resources on the work machine.
        @return: The Response from the Server.
        """

    @abstractmethod
    def unregister_self(self, uid: str) -> ServerResponse:
        """!
        Unregisters the worker client from the worker client pool of the
        central server. The server will stop dispatching new jobs to this
        machine. Once all jobs currently dispatched to this machine have
        finished, this method returns.
        @param uid: ID of the work machine.
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

    def register_self(self, uid: str, work_machine_resources: WorkMachineResources) -> ServerResponse:
        pass

    def unregister_self(self, uid: str) -> ServerResponse:
        pass

    def notify_job_finished(self, uid: str) -> ServerResponse:
        pass

    def notify_job_crashed(self, uid: str) -> ServerResponse:
        pass
