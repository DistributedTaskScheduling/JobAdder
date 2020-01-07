from datetime import datetime
from ja.common.job import Job
from ja.server.database.types.work_machine import WorkMachine


class JobRuntimeStatistics:
    """
    A collection of statistics about the job's running time, queued time, etc.
    """
    def __init__(self,
                 added: datetime,
                 started: datetime,
                 running_time: int):
        """!
        @param added The date and time when the job was first added in the database.
        @param started The date and time when the job was first started, or None if the job has never been started.
        @param The amount of time that the job has been running for, in seconds.
        """

    @property
    def time_added(self) -> datetime:
        """!
        @return The date and time when the job entry was first added.
        """

    @property
    def time_started(self) -> datetime:
        """!
        @return The date and time when the job was started for the first time,
           or None if the job has not been started yet.
        """

    @property
    def running_time(self) -> int:
        """!
        @return The amount of time that the job has been running for, in seconds.
        """


class DatabaseJobEntry:
    """
    A job entry in the database.
    """
    def __init__(self,
                 job: Job,
                 stats: JobRuntimeStatistics,
                 machine: WorkMachine):
        """!
        Construct a new database job entry.

        @param job The job stored in the database entry.
        @param stats The statistics about the job runtime stored in the database.
        @param machine The work machine this job has been assigned to, if any.
        """

    @property
    def job(self) -> Job:
        """!
        @return The job stored in this database entry.
        """

    @property
    def statistics(self) -> JobRuntimeStatistics:
        """!
        @return The statistics about the job stored in the database.
        """

    @property
    def assigned_machine(self) -> WorkMachine:
        """!
        @return The assigned work machine of the job, or None if the job is not currently running on any machine.
        """
