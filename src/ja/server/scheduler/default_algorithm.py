from typing import List, Optional, Tuple
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import SchedulingAlgorithm, CostFunction, JobDistributionPolicy


class DefaultCostFunction(CostFunction):
    """
    The default cost function provided by JobAdder.
    """

    def calculate_cost(self, job: Job) -> int:
        pass

    @property
    def blocking_threshold(self) -> int:
        pass

    @property
    def preempting_threshold(self) -> int:
        pass


class DefaultJobDistributionPolicy(JobDistributionPolicy):
    """
    The default job distribution policy provided by JobAdder.
    """

    def __init__(self, cost_function: CostFunction):
        """!
        Create a DefaultJobDistributionPolicy.

        @param cost_function The cost function to use.
        """

    def _assign_machine_cost(self, job: Job, machine: WorkMachine) -> Optional[int]:
        """!
        Calculate the cost of scheduling @job on @machine without preemption.
        @return The cost, or None if @job can not be scheduled on @machine without preemption.
        """

    def _assign_blocked_machine_cost(self, job: Job, machine: WorkMachine, existing_jobs: List[Job]) -> Optional[int]:
        """!
        Calculate the cost of assigned @machine as blocked for @job.
        @return The cost, of None if @job can not be scheduled on @machine.
        """

    def _assign_machine_preemptive_cost(self,
                                        job: Job,
                                        machine: WorkMachine,
                                        existing_jobs: List[Job]) -> Optional[Tuple[int, List[Job]]]:
        """!
        Calculate the cost of assigning @machine for @job with preemption.
        @return The cost of assigning @job to @machine and a list of jobs on @machine to preempt, or None if this is
          not possible.
        """

    def assign_machine(self, job: Job, available_machines: List[WorkMachine]) -> WorkMachine:
        pass

    def assign_blocked_machine(self,
                               job: Job,
                               distribution: ServerDatabase.JobDistribution,
                               available_machines: List[WorkMachine]) -> WorkMachine:
        pass

    def assign_machine_preemptive(self,
                                  job: Job,
                                  distribution: ServerDatabase.JobDistribution,
                                  available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        pass


class DefaultSchedulingAlgorithm(SchedulingAlgorithm):
    """
    The default scheduling algorithm used in JobAdder.
    """

    def __init__(self,
                 cost_function: CostFunction = DefaultCostFunction(),
                 distribution_policy: JobDistributionPolicy = DefaultJobDistributionPolicy(DefaultCostFunction())):
        """!
        Initialize the scheduling algorithm.

        @param cost_function The cost function to use.
        """

    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine]) \
            -> ServerDatabase.JobDistribution:
        pass
