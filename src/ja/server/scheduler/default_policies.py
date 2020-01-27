from abc import ABC, abstractmethod
from copy import deepcopy
from ja.common.job import Job, JobPriority
from ja.common.work_machine import ResourceAllocation
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import CostFunction, JobDistributionPolicy
from typing import Dict, List, Optional, Tuple

import datetime as dt


class DefaultCostFunction(CostFunction):
    """
    The default cost function provided by JobAdder.
    """
    _base_costs: Dict[JobPriority, float] = {
        JobPriority.URGENT: 0,
        JobPriority.HIGH: 500,
        JobPriority.MEDIUM: 1000,
        JobPriority.LOW: 2000,
    }
    _multiplier: float = -1

    def calculate_cost(self, job: DatabaseJobEntry) -> float:
        elapsed = int((dt.datetime.now() - job.statistics.time_added).total_seconds() / 60)
        base = self._base_costs[job.job.scheduling_constraints.priority]
        return base + self._multiplier * elapsed

    @property
    def blocking_threshold(self) -> float:
        high_base = self._base_costs[JobPriority.HIGH]
        # Start blocking if a high priority job has been around for longer than 6 hours
        return high_base + self._multiplier * 60 * 6

    @property
    def preempting_threshold(self) -> float:
        return self._base_costs[JobPriority.URGENT]


class DefaultJobDistributionPolicyBase(JobDistributionPolicy, ABC):
    """
    A base class for the default distribution policies in JobAdder.
    """
    @abstractmethod
    def _assign_machine_cost(self,
                             job: DatabaseJobEntry,
                             machine: WorkMachine,
                             existing_jobs: List[DatabaseJobEntry]) -> Optional[Tuple[float, List[Job]]]:
        """!
        Calculate the cost of assigning @machine for @job.
        @return The cost of assigning @job to @machine and a list of jobs on @machine to preempt, or None if this is
          not possible.
        """

    def _get_job_allocation(self, job: Job) -> ResourceAllocation:
        return ResourceAllocation(job.docker_constraints.cpu_threads, job.docker_constraints.memory, 0)

    def _check_machine_feasible(self, job: Job, machine: WorkMachine, free_only: bool) -> bool:
        """
        Check whether the work machine has enough resources to run the given job.
        @param free_only If True, only the free resources on the machine are taken into consideration.
        @return True if feasible, False otherwise.
        """
        if free_only:
            return machine.resources.allocate(self._get_job_allocation(job), test_only=True)
        return not (machine.resources.total_resources - self._get_job_allocation(job)).is_negative()

    def assign_machine(self,
                       job: DatabaseJobEntry,
                       distribution: ServerDatabase.JobDistribution,
                       available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        chosen_machine: Tuple[WorkMachine, List[Job]] = None
        chosen_cost: float = 0

        for machine in available_machines:
            job_entries = \
                list(filter(lambda e: ((e.assigned_machine.uid if e.assigned_machine else None) == machine.uid),
                     distribution))

            result = self._assign_machine_cost(job, machine, job_entries)
            if result:
                (cost, preempted) = result
                if not chosen_machine or cost < chosen_cost:
                    chosen_cost = cost
                    chosen_machine = (machine, preempted)
        return chosen_machine


class DefaultNonPreemptiveDistributionPolicy(DefaultJobDistributionPolicyBase):
    _cpu_threads_w = 2.0
    _memory_w = 1.0
    """
    Default distribution policy for non-preemptive scheduling.
    """
    def __init__(self, cost_function: CostFunction):
        """
        Initialize the distribution policy.
        @param cost_function The cost function to use to determine urgent jobs.
        """
        self._cost_func = cost_function

    def _assign_machine_cost(self,
                             job: DatabaseJobEntry,
                             machine: WorkMachine,
                             existing_jobs: List[DatabaseJobEntry]) -> Optional[Tuple[float, List[Job]]]:
        if not self._check_machine_feasible(job.job, machine, free_only=True):
            return None
        if machine.resources.free_resources.swap < job.job.docker_constraints.memory:
            if self._cost_func.calculate_cost(job) > self._cost_func.preempting_threshold:
                return None

        after_allocation = machine.resources.free_resources - self._get_job_allocation(job.job)
        return (after_allocation.cpu_threads * self._cpu_threads_w + after_allocation.memory * self._memory_w, [])


class DefaultBlockingDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for blocking jobs.
    """
    def _assign_machine_cost(self,
                             job: DatabaseJobEntry,
                             machine: WorkMachine,
                             existing_jobs: List[DatabaseJobEntry]) -> Optional[Tuple[float, List[Job]]]:
        if not self._check_machine_feasible(job.job, machine, free_only=False):
            return None
        return (len(existing_jobs), [])


class DefaultPreemptiveDistributionPolicy(DefaultJobDistributionPolicyBase):
    _inverse_multiplier = 10.0
    """
    Default distribution policy for preemptive jobs.
    """
    def __init__(self, cost_function: CostFunction):
        """!
        Initialize the default preemptive distribution policy.

        @param cost_function The cost function to assing priorities to tasks.
        """
        self._cost_func = cost_function

    def _assign_machine_cost(self,
                             job: DatabaseJobEntry,
                             machine: WorkMachine,
                             existing_jobs: List[DatabaseJobEntry]) -> Optional[Tuple[float, List[Job]]]:
        if not self._check_machine_feasible(job.job, machine, free_only=False):
            return None

        sorted_jobs = sorted(existing_jobs, key=lambda je: (self._cost_func.calculate_cost(je)), reverse=True)
        sorted_jobs = list(filter(lambda je: (not je.job.scheduling_constraints.is_preemptible), sorted_jobs))
        job_allocation = self._get_job_allocation(job.job)
        allocation = deepcopy(machine.resources.free_resources)

        total_cost: float = 0
        to_preempt: List[Job] = []
        while (allocation - job_allocation).is_negative():
            if not sorted_jobs:
                return None

            next_job = sorted_jobs.pop(0)
            next_job_cost = self._cost_func.calculate_cost(next_job)
            if next_job_cost <= self._cost_func.preempting_threshold:
                # We cannot pause enough jobs on this machine
                return None

            total_cost += self._inverse_multiplier / (next_job_cost - self._cost_func.preempting_threshold)
            to_preempt.append(next_job.job)
            allocation += self._get_job_allocation(next_job.job)

        return (total_cost, to_preempt)
