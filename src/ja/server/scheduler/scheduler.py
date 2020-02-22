from copy import deepcopy
from ja.common.job import JobStatus
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.dispatcher.dispatcher import Dispatcher
from ja.server.scheduler.algorithm import SchedulingAlgorithm, get_allocation_for_job
from typing import Dict


class Scheduler:
    """
    Scheduler is a class which is responsible for generating the new job
    distribution whenever the database changes.

    Internally it uses a SchedulingAlgorithm to determine how to schedule
    jobs which are still runnable.
    """

    def __init__(self, algorithm: SchedulingAlgorithm, dispatcher: Dispatcher, special_resources: Dict[str, int]):
        """!
        Initialize a Scheduler.

        @param algorithm The scheduling algorithm to use to assign jobs to work machines.
        @param dispatcher The dispatcher to use for sending commands to the work machines.
        @param special_resources The available special resources.
        """
        self._algorithm = algorithm
        self._dispatcher = dispatcher
        self._special_resources = deepcopy(special_resources)
        self._total_special_resources = deepcopy(special_resources)

    @property
    def special_resources(self) -> Dict[str, int]:
        """!
        The amount of free special resources.
        """
        return self._special_resources

    @property
    def total_special_resources(self) -> Dict[str, int]:
        """!
        The total amount of special resources.
        """
        return self._total_special_resources

    def reschedule(self, database: ServerDatabase) -> None:
        """!
        Fetches the current schedule from the database and redistributes the jobs using the scheduling algorithm.
        Then each modified job and work machine are updated in the database.

        @param database The database to fetch job schedule from.
        """
        available_machines = list(filter(lambda m: m.state == WorkMachineState.ONLINE, database.get_work_machines()))
        new_schedule = self._algorithm.reschedule_jobs(database.get_current_schedule(),
                                                       available_machines, self.special_resources)

        # Reset resources and recalculate them
        for machine in available_machines:
            machine.resources.deallocate(machine.resources.total_resources - machine.resources.free_resources)
        self._special_resources = deepcopy(self._total_special_resources)

        for job in new_schedule:
            if not job.assigned_machine:
                assert job.job.status == JobStatus.QUEUED
                continue

            database.update_job(job.job)
            database.assign_job_machine(job.job, job.assigned_machine)

            machine = next(m for m in available_machines if m.uid == job.assigned_machine.uid)
            machine.resources.allocate(get_allocation_for_job(job.job))
            for resource in job.job.scheduling_constraints.special_resources:
                assert resource in self._special_resources
                self._special_resources[resource] -= 1

        for machine in available_machines:
            database.update_work_machine(machine)

        self._dispatcher.set_distribution(new_schedule)
