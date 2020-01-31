from typing import Dict
from ja.common.config import Config
from ja.common.proxy.ssh import SSHConfig
from ja.common.work_machine import ResourceAllocation
from ja.worker.config import WorkerConfig
from unittest import TestCase


class WorkMachineConfigTest(TestCase):
    """
    Class for testing Work Machine Config
    """
    def setUp(self) -> None:
        ssh_config: SSHConfig = SSHConfig(hostname="127.0.1.1", username="someuser")
        resource_allocation: ResourceAllocation = ResourceAllocation(1, 2, 3)
        self._wmc: WorkerConfig = WorkerConfig(3, ssh_config, resource_allocation)

    def test_uid_getter(self) -> None:
        self.assertEqual(self._wmc.uid, 3)

    def test_ssh_getter(self) -> None:
        self.assertEqual(self._wmc.ssh_config.username, "someuser")
        self.assertEqual(self._wmc.ssh_config.hostname, "127.0.1.1")

    def test_resource_getter(self) -> None:
        self.assertEqual(self._wmc.resources.cpu_threads, 1)
        self.assertEqual(self._wmc.resources.memory, 2)
        self.assertEqual(self._wmc.resources.swap, 3)
