from copy import deepcopy
from ja.common.job import JobStatus
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachineState, WorkMachine
from ja.server.dispatcher.dispatcher import Dispatcher
from ja.server.scheduler.algorithm import SchedulingAlgorithm, get_allocation_for_job
from typing import Dict, List


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

    def _update_special_resources(self, actual_distribution: ServerDatabase.JobDistribution) -> None:
        self._special_resources = deepcopy(self._total_special_resources)
        for job in actual_distribution:
            if job.job.status in [JobStatus.RUNNING, JobStatus.PAUSED]:
                for resource in job.job.scheduling_constraints.special_resources:
                    assert resource in self._special_resources
                    self._special_resources[resource] -= 1

    def _recalculate_machine_resources(self, actual_distribution: ServerDatabase.JobDistribution,
                                       machines: List[WorkMachine]) -> None:
        # Reset resources and recalculate them
        for machine in machines:
            machine.resources.deallocate(machine.resources.total_resources - machine.resources.free_resources)

        # Note we don't get done/crashed for cancelled jobs, so we should mark them as freed here
        for job in actual_distribution:
            if not job.assigned_machine:
                assert job.job.status == JobStatus.QUEUED
                continue

            machine = next(m for m in machines if m.uid == job.assigned_machine.uid)
            machine.resources.allocate(get_allocation_for_job(job.job))

    def reschedule(self, database: ServerDatabase) -> None:
        """!
        Fetches the current schedule from the database and redistributes the jobs using the scheduling algorithm.
        Then each modified job and work machine are updated in the database.

        @param database The database to fetch job schedule from.
        """
        available_machines = list(filter(lambda m: m.state == WorkMachineState.ONLINE, database.get_work_machines()))

        current_schedule = database.get_current_schedule()
        cancelled_entries = [je for je in current_schedule if je.job.status == JobStatus.CANCELLED]
        runnable_entries = [je for je in current_schedule if je.job.status in
                            [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.PAUSED]]

        self._update_special_resources(runnable_entries)
        self._recalculate_machine_resources(runnable_entries, available_machines)
        new_schedule = self._algorithm.reschedule_jobs(runnable_entries, available_machines, self.special_resources)

        self._recalculate_machine_resources(new_schedule, available_machines)
        for job in new_schedule:
            if job.assigned_machine:
                database.update_job(job.job)
                database.assign_job_machine(job.job, job.assigned_machine)

        for machine in available_machines:
            database.update_work_machine(machine)

        self._update_special_resources(new_schedule)
        lost_wms = self._dispatcher.set_distribution(new_schedule + cancelled_entries)
        for wm in lost_wms:
            crashed_jobs = [entry.job for entry in runnable_entries
                            if job.assigned_machine and job.assigned_machine.uid == wm.uid]
            for crashed_job in crashed_jobs:
                crashed_job.status = JobStatus.CRASHED
                database.update_job(crashed_job)
                database.assign_job_machine(crashed_job, None)

            wm.state = WorkMachineState.OFFLINE
            wm.resources.deallocate(wm.resources.total_resources - wm.resources.free_resources)
            database.update_work_machine(wm)

        for job in cancelled_entries:
            database.assign_job_machine(job.job, None)
