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
        @param running_time The amount of time that the job has been running for, in seconds.
        """
        if running_time < 0:
            raise ValueError("Running time must be positive!")

        if added > started:
            raise ValueError("Cannot start job before adding it, added must be smaller than started!")

        self._added = added
        self._started = started
        self._running_time = running_time

    @property
    def time_added(self) -> datetime:
        """!
        @return The date and time when the job entry was first added.
        """
        return self._added

    @property
    def time_started(self) -> datetime:
        """!
        @return The date and time when the job was started for the first time,
           or None if the job has not been started yet.
        """
        return self._started

    @property
    def running_time(self) -> int:
        """!
        @return The amount of time that the job has been running for, in seconds.
        """
        return self._running_time


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
        self._job = job
        self._stats = stats
        self._machine = machine

    @property
    def job(self) -> Job:
        """!
        @return The job stored in this database entry.
        """
        return self._job

    @property
    def statistics(self) -> JobRuntimeStatistics:
        """!
        @return The statistics about the job stored in the database.
        """
        return self._stats

    @property
    def assigned_machine(self) -> WorkMachine:
        """!
        @return The assigned work machine of the job, or None if the job is not currently running on any machine.
        """
        return self._machine
