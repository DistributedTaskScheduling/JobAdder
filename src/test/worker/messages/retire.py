from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState, WorkMachineResources
from test.serializable.base import AbstractSerializableTest
from ja.worker.message.retire import RetireWorkerCommand
from ja.common.proxy.ssh import SSHConfig


class RetireMessageTest(AbstractSerializableTest):

    def setUp(self) -> None:
        self._optional_properties = []
        self._object = RetireWorkerCommand("52")
        self._object_dict = {"uid": "52"}
        self._other_object_dict = {"uid": "41"}

    def test_offline(self) -> None:
        mock_database = MockDatabase()
        work_machine = WorkMachine("machi1", WorkMachineState.ONLINE,
                                   WorkMachineResources(ResourceAllocation(12, 32, 12)),
                                   SSHConfig(
                                       hostname="www.com", username="tux",
                                       password="1235", key_filename="~/my_key.rsa",
                                       passphrase="asdfgjk")
                                   )
        mock_database.update_work_machine(work_machine)
        command = RetireWorkerCommand("machi1")
        command.execute(mock_database)
        self.assertEqual(mock_database.get_all_work_machines()[0].state, WorkMachineState.OFFLINE)

    def test_retired(self) -> None:
        mock_database = MockDatabase()
        work_machine = WorkMachine("machi1", WorkMachineState.ONLINE,
                                   WorkMachineResources(ResourceAllocation(12, 32, 12)),
                                   SSHConfig(
                                       hostname="www.com", username="tux",
                                       password="1235", key_filename="~/my_key.rsa",
                                       passphrase="asdfgjk")
                                   )
        work_machine.resources.allocate(ResourceAllocation(1, 1, 0))
        mock_database.update_work_machine(work_machine)
        command = RetireWorkerCommand("machi1")
        command.execute(mock_database)
        self.assertEqual(mock_database.get_all_work_machines()[0].state, WorkMachineState.RETIRED)
