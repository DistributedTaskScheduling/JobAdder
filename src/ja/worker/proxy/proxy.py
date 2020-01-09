from ja.common.proxy.proxy import ContinuousProxy
from ja.common.message.server import ServerResponse
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachineResources


class WorkerServerProxy(ContinuousProxy):
    """
    Proxy for the central server used on the worker client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko
        """

    def register_self(self, work_machine_resources: WorkMachineResources) -> ServerResponse:
        """!
        Adds the worker client to the worker client pool of the central server.
        The server will establish an SSHConnection to the worker client and
        begin sending WorkerCommands.
        @param work_machine_resources: The resources available on this work machine.
        @return: The Response from the Server.
        """

    def unregister_self(self) -> ServerResponse:
        """!
        Unregisters the worker client from the worker client pool of the
        central server. The server will stop dispatching new jobs to this
        machine. Once all jobs currently dispatched to this machine have
        finished, this method returns.
        @return: The Response from the Server.
        """

    def notify_job_finished(self, uid: str) -> ServerResponse:
        """!
        @param uid: uid of the job that has finished.
        @return: The Response from the Server.
        """

    def notify_job_crashed(self, uid: str) -> ServerResponse:
        """!
        @param uid: uid of the job that has crashed.
        @return: The Response from the Server.
        """
