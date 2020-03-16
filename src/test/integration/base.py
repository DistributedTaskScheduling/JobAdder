from unittest import TestCase
from typing import List
from pathlib import Path
from threading import Thread
from getpass import getuser
from time import sleep

from ja.server.database.types.work_machine import WorkMachine
from ja.worker.main import JobWorker
from ja.common.proxy.ssh import SSHConfig, ISSHConnection, SSHConnection
from ja.common.work_machine import ResourceAllocation
from ja.user.cli import UserClientCLIHandler
from ja.server.main import JobCenter
from ja.server.config import ServerConfig, LoginConfig
from ja.worker.config import WorkerConfig
from ja.server.proxy.proxy import WorkerProxyBase, IWorkerProxy
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase


DATABASE_NAME = "jobadder-test"
TESTING_DIRECTORY = "/var/tmp/jobadder/"
SERVER_CONF_PATH = TESTING_DIRECTORY + "server.conf"
WORKER_CONF_PATH = TESTING_DIRECTORY + "worker-%s.conf"
SSH_CONF_PATH = TESTING_DIRECTORY + "ssh.conf"
SERVER_SOCKET_PATH = TESTING_DIRECTORY + "server.socket"
WORKER_SOCKET_PATH = TESTING_DIRECTORY + "worker-%s.socket"
SERVER_REMOTE_MODULE = "test.integration.remote.server"
WORKER_REMOTE_MODULE = "test.integration.remote.%s"
if getuser() == "travis":
    COMMAND_STRING = "~/virtualenv/python3.7/bin/python3 -m %s"
else:
    COMMAND_STRING = "python3 -m %s"


class TestWorkerProxy(WorkerProxyBase):

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnection(
            ssh_config=ssh_config,
            remote_module=WORKER_REMOTE_MODULE % self._uid,
            command_string=COMMAND_STRING
        )


class TestWorkerProxyFactory(WorkerProxyFactoryBase):

    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        return TestWorkerProxy(uid=work_machine.uid, ssh_config=None)  # FIXME need to get worker ssh config


class TestJobCenter(JobCenter):

    @staticmethod
    def _read_config() -> ServerConfig:
        with open(SERVER_CONF_PATH) as f:
            return ServerConfig.from_string(f.read())

    def _get_proxy_factory(self) -> WorkerProxyFactoryBase:
        return TestWorkerProxyFactory(self._database)


class TestJobWorker(JobWorker):
    def __init__(self, index: int):
        self._index = index
        super().__init__(
            config_path=WORKER_CONF_PATH % self._index, socket_path=WORKER_SOCKET_PATH,
            remote_module=SERVER_REMOTE_MODULE, command_string=COMMAND_STRING)


class IntegrationTest(TestCase):

    def setUp(self) -> None:
        Path(TESTING_DIRECTORY).mkdir(parents=True, exist_ok=True)
        with open(SERVER_CONF_PATH, "w") as f:
            f.write(str(self.server_config))
        self._server = TestJobCenter(socket_path=SERVER_SOCKET_PATH, database_name=DATABASE_NAME)
        Thread(target=self._server.run, name="server-main", daemon=True).start()

        with open(SSH_CONF_PATH, "w") as f:
            f.write(str(self.ssh_config))

        self._clients: List[UserClientCLIHandler] = []
        for i in range(self.num_clients):
            client = UserClientCLIHandler(config_path=SSH_CONF_PATH)
            self._clients.append(client)

        self._workers: List[JobWorker] = []
        for i in range(self.num_workers):
            with open(WORKER_CONF_PATH % i, "w") as f:
                f.write(str(self.get_worker_config(i)))
            worker = TestJobWorker(index=i)
            Thread(target=worker.run, name="worker-%s" % i, daemon=True).start()
            self._workers.append(worker)
        sleep(1)

    def tearDown(self) -> None:
        self._server._database.delete_all_records()
        self._server._database.__del__()

    @property
    def ssh_config(self) -> SSHConfig:
        return SSHConfig(hostname="localhost", username=getuser())

    @property
    def server_config(self) -> ServerConfig:
        database_config = LoginConfig(host="localhost", port=None, username="jobadder", password="")
        email_config = LoginConfig(host="localhost", port=1337, username="", password="")
        return ServerConfig(
            admin_group="jobadder", database_config=database_config, email_config=email_config,
            special_resources=dict(), blocking_enabled=True, preemption_enabled=True, web_server_port=0
        )

    def get_worker_config(self, index: int) -> WorkerConfig:
        return WorkerConfig(
            uid="worker%s" % index, ssh_config=self.ssh_config,
            resource_allocation=self.get_resource_allocation(index), admin_group="jobadder"
        )

    def get_resource_allocation(self, index: int) -> ResourceAllocation:
        return ResourceAllocation(cpu_threads=4, memory=16 * 1024, swap=16 * 1024)

    @property
    def num_clients(self) -> int:
        return 1

    @property
    def num_workers(self) -> int:
        return 1

    def test_sanity_checks(self) -> None:
        self.assertEqual(len(self._server._database.get_work_machines()), self.num_workers)