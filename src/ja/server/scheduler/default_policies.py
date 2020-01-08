from abc import ABC, abstractmethod
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import CostFunction, JobDistributionPolicy
from typing import List, Optional, Tuple


class DefaultCostFunction(CostFunction):
    """
    The default cost function provided by JobAdder.
    """

    def calculate_cost(self, job: Job) -> float:
        pass

    @property
    def blocking_threshold(self) -> float:
        pass

    @property
    def preempting_threshold(self) -> float:
        pass


class DefaultJobDistributionPolicyBase(JobDistributionPolicy, ABC):
    """
    A base class for the default distribution policies in JobAdder.
    """
    @abstractmethod
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[int, List[Job]]]:
        """!
        Calculate the cost of assigning @machine for @job.
        @return The cost of assigning @job to @machine and a list of jobs on @machine to preempt, or None if this is
          not possible.
        """

    def assign_machine(self,
                       job: Job,
                       distribution: ServerDatabase.JobDistribution,
                       available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        # Should iterate over all available machines and select the best one depending on _assign_machine_cost
        pass


class DefaultNonPreemptiveDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for non-preemptive scheduling.
    """
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[int, List[Job]]]:
        pass


class DefaultBlockingDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for blocking jobs.
    """
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[int, List[Job]]]:
        pass


class DefaultPreemptiveDistributionPolicy(DefaultJobDistributionPolicyBase):
    """
    Default distribution policy for preemptive jobs.
    """
    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[Job]) -> Optional[Tuple[int, List[Job]]]:
        pass
