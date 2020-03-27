from abc import ABC
from ja.common.job import JobStatus
from ja.common.message.server import ServerCommand
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.scheduler.algorithm import get_allocation_for_job


class WorkerServerCommand(ServerCommand, ABC):
    """
    Base class for server commands sent by worker clients.
    """
    @staticmethod
    def _free_resources_for_job(db: ServerDatabase, job_entry: DatabaseJobEntry, status: JobStatus) -> None:
        resources = get_allocation_for_job(job_entry.job)
        job_entry.job.status = status

        db.update_job(job_entry.job)
        machine = job_entry.assigned_machine
        db.assign_job_machine(job_entry.job, None)

        if machine is not None:
            machine.resources.deallocate(resources)
            if machine.state is WorkMachineState.RETIRED:
                if machine.resources.free_resources == machine.resources.total_resources:
                    # No more jobs on this work machine
                    machine.state = WorkMachineState.OFFLINE

            db.update_work_machine(machine)
