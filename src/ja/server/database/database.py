from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Callable
from ja.common.job import Job
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine


class ServerDatabase(ABC):
    """!
    ServerDatabase is the interface which a database used by JobAdder needs to implement.
    """

    @abstractmethod
    def find_job_by_id(self, job_id: str) -> DatabaseJobEntry:
        """!
        Load a job from the database by its id.

        @param job_id The id of the job.
        @return The stored data about the job, or None if no such job was found.
        """

    @abstractmethod
    def find_job_by_label(self, label: str) -> Job:
        """!
        Load a job from the database by its label.

        @param label label of the job.
        @return The stored data about the job, or None if no such job was found.
        """

    @abstractmethod
    def update_job(self, job: Job) -> None:
        """!
        Update the job in the database.
        If no job with the id of @job has been stored up to now, a new entry will be created in the database.

        @param job The job to update stored data for.
        """

    @abstractmethod
    def assign_job_machine(self, job: Job, machine: WorkMachine) -> None:
        """!
        Update the job's assigned work machine in the database.
        This will cause a RuntimeError if the job is not in the database.

        @param job The job to change assigned work machine for.
        @param machine The work machine the job is assigned to, or None.
        """

    @abstractmethod
    def update_work_machine(self, machine: WorkMachine) -> None:
        """!
        Update the stored data about the given work machine.
        If there is no entry in the database for the given work machine, a new entry will be added.

        @param machine The machine to update data for.
        """

    @abstractmethod
    def get_work_machines(self) -> List[WorkMachine]:
        """!
        @return A list of online work machines.
        """

    JobDistribution = List[DatabaseJobEntry]

    @abstractmethod
    def get_current_schedule(self) -> JobDistribution:
        """!
        Generate a list of all jobs which are in state NEW, QUEUED, PAUSED and RUNNING, as well as jobs which still
        have an assigned work machine.

        Each job is paired with its assigned work machine, if such a machine exists.

        @return A list of all scheduleable and scheduled jobs, with their assigned work machines.
        """

    @abstractmethod
    def query_jobs(self, since: datetime, user_id: int, work_machine: WorkMachine) -> List[DatabaseJobEntry]:
        """!
        Generate a list of all jobs belonging to @user_id since @since which are or have been running on @workmachine.

        @param since Date and time of the oldest interesting job, or None if the query is not limited to any given
          interval of time.
        @param user_id The user to query jobs for, or -1 if the query is for all users.
        @param work_machine The work machine to query jobs for, or None if the query is for all work machines.

        @return A list of the jobs which fall into the criteria above.
        """

    RescheduleCallback = Callable[['ServerDatabase'], None]

    @abstractmethod
    def set_scheduler_callback(self, callback: RescheduleCallback) -> None:
        """!
        Set a function which will be called whenever the database is updated and this update makes rescheduling
        @param callback The callback to execute when rescheduling is necessary.
        """

    JobStatusCallback = Callable[['Job'], None]

    @abstractmethod
    def set_job_status_callback(self, callback: JobStatusCallback) -> None:
        """!
        Set a function which will be called whenever a job in the database is updated and its status changes.

        @param callback The callback to execute when an update happens.
        """
