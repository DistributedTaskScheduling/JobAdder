from ja.common.proxy.ssh import SSHConfig
from ja.common.work_machine import ResourceAllocation
from ja.worker.config import WorkerConfig
from test.serializable.base import AbstractSerializableTest
from unittest import TestCase
from typing import Dict


class WorkMachineConfigTest(TestCase):
    """
    Class for testing Work Machine Config
    """
    def setUp(self) -> None:
        ssh_config: SSHConfig = SSHConfig(hostname="127.0.1.1", username="someuser")
        resource_allocation: ResourceAllocation = ResourceAllocation(1, 2, 3)
        self._wmc: WorkerConfig = WorkerConfig("3", ssh_config, resource_allocation, "127.0.1.1")

    def test_uid_getter(self) -> None:
        self.assertEqual(self._wmc.uid, "3")

    def test_ip_getter(self) -> None:
        self.assertEqual(self._wmc.ip, "127.0.1.1")

    # def test_ssh_getter(self) -> None:
    #    self.assertEqual(self._wmc.ssh_config.username, "someuser")
    #    self.assertEqual(self._wmc.ssh_config.hostname, "127.0.1.1")

    def test_resource_getter(self) -> None:
        self.assertEqual(self._wmc.resources.cpu_threads, 1)
        self.assertEqual(self._wmc.resources.memory, 2)
        self.assertEqual(self._wmc.resources.swap, 3)

    def test_from_dict(self) -> None:
        d: Dict[str, object] = dict()
        d["ssh_config"] = self._wmc.ssh_config.to_dict()
        d["resource_allocation"] = self._wmc.resources.to_dict()
        d["uid"] = self._wmc.uid
        # self.assertDictEqual(self._wmc, d)
        # wc = WorkerConfig.from_dict(d)
        # self.assertDictEqual(wc, d)


class WorkerMachineDictTest(AbstractSerializableTest):
    """
    using the AbstractSerializableTest tests
    """

    def setUp(self) -> None:
        self._optional_properties = []
        self._object = WorkerConfig(ssh_config=SSHConfig(hostname="127.0.1.1", username="someuser"),
                                    resource_allocation=ResourceAllocation(1, 2, 3), uid="3")
        self._object_dict = {
            "uid": "3",
            "ssh_config": {
                "hostname": "127.0.1.1",
                "username": "someuser"
            },
            "resource_allocation": {
                "cpu_threads": 1,
                "memory": 2,
                "swap": 3
            }
        }
        self._other_object_dict = {
            "uid": "4",
            "ssh_config": {
                "hostname": "127.0.1.2",
                "username": "someuser"
            },
            "resource_allocation": {
                "cpu_threads": 1,
                "memory": 2,
                "swap": 3
            }
        }
