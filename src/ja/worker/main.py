"""
Contains classes needed by each WC for providing a DockerClient as well
as notifying the CS
"""
from typing import cast

from ja.server.database.types.work_machine import WorkMachineResources
from ja.worker.config import WorkerConfig
from ja.worker.proxy.proxy import WorkerServerProxy
from ja.worker.docker import DockerInterface
from ja.worker.proxy.command_handler import WorkerCommandHandler

import time
import logging
logger = logging.getLogger(__name__)


class JobWorker:
    """
    The main class on the Worker Client
    """
    def __init__(
            self, config_path: str = "/etc/jobadder/worker.conf",
            socket_path: str = "/tmp/jobadder-worker.socket",
            remote_module: str = "ja.server.proxy.remote",
            command_string: str = "python3 -m %s") -> None:
        """!
        Reads a WorkerConfig object from the disk.
        Creates WorkerServerProxy, DockerInterface, WorkerCommandHandler objects.
        @param config_path: the path to read a WorkerConfig object from.
        @param socket_path: the path of the socket to listen on for commands.
        @param remote_module: the module to execute on the server.
        @param command_string: the command template to execute on the server.
        """
        logger.info("Using worker config file %s." % config_path)
        self._config_path = config_path
        with open(self._config_path, "r") as f:
            self._config = cast(WorkerConfig, WorkerConfig.from_string(f.read()))

        self._server_proxy = WorkerServerProxy(
            ssh_config=self._config.ssh_config, remote_module=remote_module, command_string=command_string)
        self._docker_interface = DockerInterface(self._server_proxy, worker_uid=self._config.uid)
        self._command_handler = WorkerCommandHandler(
            admin_group=self._config.admin_group, docker_interface=self._docker_interface, socket_path=socket_path)

    def run(self) -> None:
        """
        Registers this worker on the central server and starts the  main loop of the command handler.
        """
        register_response = self._server_proxy.register_self(
            uid=self._config.uid, work_machine_resources=WorkMachineResources(self._config.resources))

        if not register_response.is_success:
            logger.error("Failed to register with the server at %s: %s" %
                         (self._config.ssh_config.hostname, register_response.result_string))
            return

        # If uid is unset for this worker, save the uid assigned by the server for consistency.
        if self._config.uid is None:
            self._config.uid = register_response.uid
            with open(self._config_path, "r") as f:
                f.write(str(self._config))

        logger.info("Registered with server at %s, uid: %s" % (self._config.ssh_config.hostname, self._config.uid))
        self._command_handler.main_loop()

        self._server_proxy.unregister_self(self._config.uid)
        # Wait for commands to finish, but check periodically whether all of them have finished
        while self._docker_interface.has_running_jobs():
            time.sleep(1)
