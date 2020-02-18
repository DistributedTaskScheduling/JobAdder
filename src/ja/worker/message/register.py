from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine


class RegisterWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machines exists and can process jobs.
    """

    def __init__(self, work_machine: WorkMachine):
        """!
        @param work_machine: The work machine object that represents the Worker machine.
        """
        self._work_machine = work_machine

    def __eq__(self, o: object) -> bool:
        if isinstance(o, RegisterWorkerCommand):
            return self._work_machine == o._work_machine
        return False

    @property
    def work_machine(self) -> WorkMachine:
        """!
        @return: The work machine.
        """
        return self._work_machine

    def execute(self, database: ServerDatabase) -> Response:
        work_machines = database.get_work_machines()
        for x in work_machines:
            if x.uid == self._work_machine.uid:
                return Response("", False)
        database.update_work_machine(self._work_machine)
        return Response("", True)

    def to_dict(self) -> Dict[str, object]:
        n_dict: Dict[str, object] = dict()
        n_dict["work_machine"] = self._work_machine.to_dict()
        return n_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "RegisterWorkerCommand":
        work_machine = WorkMachine.from_dict(cls._get_dict_from_dict(property_dict, key="work_machine", mandatory=True))
        cls._assert_all_properties_used(property_dict)
        return RegisterWorkerCommand(work_machine)
