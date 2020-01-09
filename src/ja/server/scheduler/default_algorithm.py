from typing import List
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import SchedulingAlgorithm, JobDistributionPolicy, CostFunction


class DefaultSchedulingAlgorithm(SchedulingAlgorithm):
    """
    The default scheduling algorithm used in JobAdder.
    """

    def __init__(self,
                 cost_function: CostFunction,
                 non_preemptive_distribution_policy: JobDistributionPolicy,
                 blocking_distribution_policy: JobDistributionPolicy,
                 preemptive_distribution_policy: JobDistributionPolicy):
        """!
        Initialize the scheduling algorithm.

        @param cost_function The cost function to use.
        @param non_preemptive_distribution_policy The policy to use when distributing jobs which cannot preempt other
          jobs. The list of jobs to be preempted returned by JobDistributionPolicy.assign_machine is ignored.
        @param blocking_distribution_policy The policy to use when choosing a machine to reserve for a blocking job.
          The list of jobs to be preempted returned by JobDistributionPolicy.assign_machine is ignored.
        @param preemptive_distribution_policy The policy to use when choosing a machine to reserve for a job which can
          preempt other jobs.
        """

    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine]) -> ServerDatabase.JobDistribution:
        pass
