from abc import ABC, abstractmethod
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
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[float, List[Job]]]:
        """!
        Calculate the cost of assigning @machine for @job.
        @return The cost of assigning @job to @machine and a list of jobs on @machine to preempt, or None if this is
          not possible.
        """

    def assign_machine(self,
                       job: Job,
                       distribution: ServerDatabase.JobDistribution,
                       available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        chosen_machine: Tuple[WorkMachine, List[Job]] = None
        chosen_cost: float = 0

        for machine in available_machines:
            job_entries = [ej.job for ej in filter(lambda entry: (entry.assigned_machine is machine), distribution)]
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
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[float, List[Job]]]:
        job_allocation = ResourceAllocation(job.docker_constraints.cpu_threads, job.docker_constraints.memory, 0)
        after_allocation = machine.resources.free_resources - job_allocation
        if after_allocation.is_negative():
            return None

        return (after_allocation.cpu_threads * self._cpu_threads_w + after_allocation.memory * self._memory_w, [])


class DefaultBlockingDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for blocking jobs.
    """
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[float, List[Job]]]:
        pass


class DefaultPreemptiveDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for preemptive jobs.
    """
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[float, List[Job]]]:
        pass
