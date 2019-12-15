from typing import List
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import SchedulingAlgorithm, CostFunction


class DefaultCostFunction(CostFunction):
    """
    The default cost function used in JobAdder.
    """
    def calculate_cost(self, job: Job) -> int:
        pass


class DefaultSchedulingAlgorithm(SchedulingAlgorithm):
    """
    The default scheduling algorithm used in JobAdder.
    """

    def __init__(self, cost_function: CostFunction = DefaultCostFunction()):
        """!
        Initialize the scheduling algorithm.

        @param cost_function The cost function to use.
        """

    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine]) \
            -> ServerDatabase.JobDistribution:
        pass
