from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine


class CostFunction(ABC):
    """
    A CostFunction is a function which determines the order in which jobs are scheduled.
    """

    @abstractmethod
    def calculate_cost(self, job: DatabaseJobEntry) -> float:
        """!
        Calculate the cost of a job.

        The cost of a job is a float. Lower values mean higher priority for
        the job when considering which jobs to schedule.

        @param job The job whose cost should be calculated.
        @return The calculated cost of the job.
        """

    @property
    @abstractmethod
    def blocking_threshold(self) -> float:
        """!
        @return The maximum cost a job can have so that it can block further
          jobs with smaller cost from being scheduled.
        """

    @property
    @abstractmethod
    def preempting_threshold(self) -> float:
        """!
        @return The maximum cost a job can have so that it can preempt already
          running jobs. Should be at most @blocking_threshold.
        """


class JobDistributionPolicy(ABC):
    """
    A JobDistributionPolicy determines which machine is chosen when a job is to be scheduled.
    """

    @abstractmethod
    def assign_machine(self,
                       job: DatabaseJobEntry,
                       distribution: ServerDatabase.JobDistribution,
                       available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        """!
        Find a machine to schedule @job on.

        @param job The job to be scheduled.
        @param available_machines A list of available work machines to assign @job on.
        @param distribution The current distribution of jobs among work machines.
        @return If there is no suitable work machine where the job should be scheduled, return None.
          Otherwise, return the assigned work machine and a list of jobs running on that machine to preempt.
        """


class SchedulingAlgorithm(ABC):
    """
    The base class for any scheduling algorithm that can be used in JobAdder.
    """

    @abstractmethod
    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine],
                        available_special_resources: Dict[str, int]) -> ServerDatabase.JobDistribution:
        """!
        Given the current list of jobs with their states and their assigned work machines, calculate the next states and
        assigned machines for these jobs.

        All jobs in the schedule have a state QUEUED, RUNNING or PAUSED, and each running or paused job is assigned to
        an online machine.

        @param current_schedule A list of jobs with their states and assigned work machine, if such a machine exists.
        @param available_machines A list of work machines which can receive new commands (i.e they are online). The
        @param available_special_resources The amount of special resources available for new jobs.

        @return The new job distribution.
        """
