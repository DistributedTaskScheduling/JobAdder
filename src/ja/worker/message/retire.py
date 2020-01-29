from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.database.types.work_machine import WorkMachineConnectionDetails


class RetireWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machine is retiring and cannot accept further jobs.
    """
    def __init__(self, work_machine_uid: str, connection_details: WorkMachineConnectionDetails):
        """!
        @param work_machine_uid: The UID of the work machine that is retiring.
        """
        self._uid = work_machine_uid
        self._connection_details = connection_details

    @property
    def work_machine_uid(self) -> str:
        """!
        @return: The UID of the work machine that is retiring.
        """
        return self._uid

    def execute(self, database: ServerDatabase) -> ServerResponse:
        wm = self.create_work_machine()
        database.update_work_machine(wm)
        return ServerResponse(result_string="machine retired", is_success=True)

    def create_work_machine(self) -> WorkMachine:
        uid = self._uid
        state = WorkMachineState.OFFLINE
        connection_details = self._connection_details
        wm = WorkMachine(uid=uid, state=state, resources=None,
                         connection=connection_details)
        return wm

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["uid"] = self._uid
        # d["connection_details"] = something()
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerServerCommand":
        uid = str(property_dict["uid"])
        # connection_details = WorkMachineConnectionDetails.from_dict(
        #    cls._get_dict_from_dict(property_dict=property_dict, key="connection_details", mandatory=False))
        return RetireWorkerCommand(uid, None)
