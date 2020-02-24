from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState, WorkMachineResources
from test.serializable.base import AbstractSerializableTest
from ja.worker.message.retire import RetireWorkerCommand


class RetireMessageTest(AbstractSerializableTest):

    def setUp(self) -> None:
        self._optional_properties = []
        self._object = RetireWorkerCommand("52")
        self._object_dict = {"uid": "52"}
        self._other_object_dict = {"uid": "41"}

    def test_command(self) -> None:
        mock_database = MockDatabase()
        work_machine = WorkMachine("machi1", WorkMachineState.ONLINE,
                                   WorkMachineResources(ResourceAllocation(12, 32, 12)))
        mock_database.update_work_machine(work_machine)
        command = RetireWorkerCommand("machi1")
        command.execute(mock_database)
        self.assertEqual(mock_database.get_work_machines()[0].state, WorkMachineState.RETIRED)
