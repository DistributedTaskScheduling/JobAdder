from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine


class CostFunction(ABC):
    """
    A CostFunction is a collection of functions which determine the order in
    which jobs are scheduled.
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

    @abstractmethod
    @property
    def blocking_threshold(self) -> int:
        """!
        @return The minimum cost a job can have so that it can block further
          jobs with smaller cost from being scheduled.
        """

    @abstractmethod
    @property
    def preempting_threshold(self) -> int:
        """!
        @return The minimum cost a job can have so that it can preempt already
          running jobs. Should be at least @blocking_threshold.
        """


class JobDistributionPolicy(ABC):
    """
    JobDistributionPolicy is a collection of functions which determine how
    jobs to be scheduled are to be distributed among work machines.
    """

    @abstractmethod
    def assign_machine(self, job: Job, available_machines: List[WorkMachine]) -> WorkMachine:
        """!
        Find a machine to schedule @job on, without preempting any existing
        jobs.

        @param job The job to be scheduled.
        @param available_machines A list of available work machines to
          schedule @job on.
        @return The chosen work machine (must be one of @available_machines),
          or None if no suitable work machine was found.
        """

    @abstractmethod
    def assign_blocked_machine(self,
                               job: Job,
                               distribution: ServerDatabase.JobDistribution,
                               available_machines: List[WorkMachine]) -> WorkMachine:
        """!
        Find a machine to reserve for @job. Reserving a machine means no more
        jobs with lower cost will be scheduled on the returned machine.

        @param job The job to be scheduled.
        @param distribution The existing distribution of jobs on work machines.
        @param available_machines A list of available work machines to
          assign as blocked for @job.
        @return The chosen work machine (must be one of @available_machines),
          or None if no suitable work machine was found.
        """

    @abstractmethod
    def assign_machine_preemptive(self,
                                  job: Job,
                                  distribution: ServerDatabase.JobDistribution,
                                  available_machines: List[WorkMachine]) -> Optional[Tuple[WorkMachine, List[Job]]]:
        """!
        Find a machine to schedule @job on, preemption of already running jobs is allowed.

        @param job The job to be scheduled.
        @param available_machines A list of available work machines to assign @job on.
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
                        available_machines: List[WorkMachine]) -> ServerDatabase.JobDistribution:
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
