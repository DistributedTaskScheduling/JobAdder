from abc import ABC, abstractmethod
from typing import List
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine


class CostFunction(ABC):
    """
    The base class for any cost function that can be used with a scheduling
    algorithm.
    """

    @abstractmethod
    def calculate_cost(self, job: Job) -> int:
        """!
        Calculate the cost of a job.

        The cost of a job is an integer. Higher values mean higher priority for
        the job when considering which jobs to schedule.

        @param job The job whose cost should be calculated.
        @return The calculated cost of the job.
        """


class SchedulingAlgorithm(ABC):
    """
    The base class for any scheduling algorithm that can be used in JobAdder.
    """

    @abstractmethod
    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine]) \
            -> ServerDatabase.JobDistribution:
        """!
        Given the current list of jobs with their states and their assigned
        work machines, calculate the next states and assigned machines for
        these jobs.

        All jobs in the schedule have a state QUEUED, RUNNING or PAUSED, and
        each running or paused job is assigned to an online machine.

        @param current_schedule A list of jobs with their states and assigned
          work machine, if such a machine exists.
        @param available_machines A list of work machines which can receive new
          commands (i.e they are online).
        """
