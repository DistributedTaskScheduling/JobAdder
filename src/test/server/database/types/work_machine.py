from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.work_machine import WorkMachineResources, WorkMachine, WorkMachineState
from unittest import TestCase


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
        self.assertIsNone(wm.resources)

    def test_resources_getter1(self) -> None:
        wmr: WorkMachineResources = WorkMachineResources(ResourceAllocation(1, 2, 3))
        wm: WorkMachine = WorkMachine("cray", WorkMachineState.RETIRED, wmr)
        self.assertEqual(wm.resources, wmr)
