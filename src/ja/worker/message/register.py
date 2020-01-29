from typing import Dict

from ja.worker.message.base import WorkerServerCommand
from ja.common.message.server import ServerResponse
from ja.server.database.database import ServerDatabase
from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.work_machine import WorkMachine
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.database.types.work_machine import WorkMachineConnectionDetails


class RegisterWorkerCommand(WorkerServerCommand):
    """
    Informs the server that this work machines exists and can process jobs.
    """
    def __init__(self, work_machine_uid: str, resources: ResourceAllocation,
                 connection_details: WorkMachineConnectionDetails):
        """!
        @param work_machine_uid: The desired UID for this work machine.
        """
        self._uid = work_machine_uid
        self._resources = resources
        self._connection_details = connection_details

    @property
    def work_machine_uid(self) -> str:
        """!
        @return: The desired UID for this work machine.
        """
        return self._uid

    def execute(self, database: ServerDatabase) -> ServerResponse:
        work_machine = self.create_work_machine()
        database.update_work_machine(work_machine)
        return ServerResponse(result_string="machine added", is_success=True)

    def create_work_machine(self) -> WorkMachine:
        uid = self._uid
        state = WorkMachineState.ONLINE
        res = self._resources
        connection_details = self._connection_details
        wm = WorkMachine(uid=uid, state=state, resources=res,
                         connection=connection_details)
        return wm

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["uid"] = self._uid
        d["resource_allocation"] = self._resource_allocation.to_dict()
        # d["connection_details"] = something() 
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "RegisterWorkerCommand":
        uid = str(property_dict["uid"])
        resource_allocation = ResourceAllocation.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="resource_allocation", mandatory=False))
        return RegisterWorkerCommand(uid, resource_allocation, None)
