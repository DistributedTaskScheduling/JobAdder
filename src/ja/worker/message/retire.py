from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState


class RetireWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machine is retiring and cannot accept further jobs.
    """

    def __init__(self, work_machine_uid: str):
        """!
        @param work_machine_uid: The UID of the work machine that is retiring.
        """
        self._work_machine_uid = work_machine_uid

    def __eq__(self, o: object) -> bool:
        if isinstance(o, RetireWorkerCommand):
            return self._work_machine_uid == o._work_machine_uid
        return False

    @property
    def work_machine_uid(self) -> str:
        """!
        @return: The UID of the work machine that is retiring.
        """
        return self._work_machine_uid

    def execute(self, database: ServerDatabase) -> Response:
        work_machines = database.get_work_machines()
        if work_machines is None:
            raise ValueError("There is no work machine with %s id on the server" % self._work_machine_uid)
        work_machine: WorkMachine = next(x for x in work_machines if x.uid == self._work_machine_uid)
        work_machine.state = WorkMachineState.RETIRED
        if work_machine.resources.total_resources == work_machine.resources.free_resources:
            work_machine.state = WorkMachineState.OFFLINE
        database.update_work_machine(work_machine)
        return Response("Successfully retired Work machine with uid: {}".format(self._work_machine_uid), True)

    def to_dict(self) -> Dict[str, object]:
        n_dict: Dict[str, object] = dict()
        n_dict["uid"] = self._work_machine_uid
        return n_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerServerCommand":
        uid = cls._get_str_from_dict(property_dict=property_dict, key="uid", mandatory=True)
        cls._assert_all_properties_used(property_dict)
        return RetireWorkerCommand(uid)
