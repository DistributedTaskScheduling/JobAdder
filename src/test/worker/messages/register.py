from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState, WorkMachineResources
from test.serializable.base import AbstractSerializableTest
from ja.worker.message.register import RegisterWorkerCommand


class RegisterWorkerTest(AbstractSerializableTest):

    def setUp(self) -> None:
        self.mock_database = MockDatabase()
        self.work_machine = WorkMachine("machi1", WorkMachineState.ONLINE,
                                        WorkMachineResources(ResourceAllocation(12, 32, 12)))
        self._optional_properties = []
        self.work_machine2 = WorkMachine("mrazqtoqpredmet", WorkMachineState.ONLINE,
                                         WorkMachineResources(ResourceAllocation(1, 2, 2)))
        self._command = RegisterWorkerCommand(self.work_machine)
        self._object = self._command
        self._object_dict = {"work_machine": self.work_machine.to_dict()}
        self._other_object_dict = {"work_machine": self.work_machine2.to_dict()}

    def test_command(self) -> None:
        self._command.execute(self.mock_database)
        self.assertEqual(self.mock_database.get_work_machines()[0].state, WorkMachineState.ONLINE)
