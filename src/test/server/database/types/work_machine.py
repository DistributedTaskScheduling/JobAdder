from ja.common.work_machine import ResourceAllocation
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachineResources, WorkMachine, WorkMachineState
from unittest import TestCase
from test.serializable.base import AbstractSerializableTest


class WorkMachineResourcesTest(TestCase):
    """
    Class for testing WorkMachineResources
    """

    def setUp(self) -> None:
        self._wmr: WorkMachineResources = WorkMachineResources(ResourceAllocation(1, 2, 3))

    def test_allocate(self) -> None:
        self._wmr.allocate(ResourceAllocation(1, 1, 1))
        self.assertEqual(self._wmr.free_resources, ResourceAllocation(0, 1, 2))

    def test_allocate_failure(self) -> None:
        self.assertFalse(self._wmr.allocate(ResourceAllocation(2, 1, 1)))

    def test_deallocate(self) -> None:
        self._wmr.allocate(ResourceAllocation(1, 1, 1))
        self._wmr.deallocate(ResourceAllocation(0, 1, 1))
        self.assertEqual(self._wmr.free_resources, ResourceAllocation(0, 2, 3))

    def test_deallocate_failure(self) -> None:
        self._wmr.allocate(ResourceAllocation(1, 1, 1))
        self.assertFalse(self._wmr.deallocate(ResourceAllocation(2, 1, 1)))


class WorkMachineTest(TestCase):
    """
    Class for testing WorkMachine database type.
    """

    def test_resources_getter(self) -> None:
        wmr: WorkMachineResources = WorkMachineResources(ResourceAllocation(1, 2, 3))
        wm: WorkMachine = WorkMachine("cray", WorkMachineState.OFFLINE, wmr)
        self.assertEqual(wm.resources, wmr)

    def test_resources_getter1(self) -> None:
        wmr: WorkMachineResources = WorkMachineResources(ResourceAllocation(1, 2, 3))
        wm: WorkMachine = WorkMachine("cray", WorkMachineState.RETIRED, wmr)
        self.assertEqual(wm.resources, wmr)


class WorkMachineSerializableTest(AbstractSerializableTest):
    def setUp(self) -> None:
        self._optional_properties = ["resources", "ssh_config"]
        self._object = WorkMachine("machina1", WorkMachineState.ONLINE,
                                   WorkMachineResources(ResourceAllocation(1, 2, 3), ResourceAllocation(0, 0, 0)),
                                   SSHConfig(
                                       hostname="www", username="tux",
                                       password="1235", key_filename="my_key",
                                       passphrase="asd"))
        self._object_dict = {
            "uid": "machina1",
            "state": 0,
            "resources": {
                "total_resources": {
                    "cpu_threads": 1,
                    "memory": 2,
                    "swap": 3
                },
                "free_resources": {
                    "cpu_threads": 0,
                    "memory": 0,
                    "swap": 0
                }
            },
            "ssh_config": {
                "hostname": "www",
                "username": "tux",
                "password": "1235",
                "key_filename": "my_key",
                "passphrase": "asd"
            }
        }
        self._other_object_dict = {
            "uid": "machi1",
            "state": 20,
            "resources": {
                "total_resources": {
                    "cpu_threads": 1,
                    "memory": 2,
                    "swap": 3
                }
            }
        }
