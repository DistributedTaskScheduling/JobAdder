from datetime import datetime
from ja.common.job import Job
from ja.server.database.types.work_machine import WorkMachine
from typing import Optional


class JobRuntimeStatistics:
    """
    A collection of statistics about the job's running time, queued time, etc.
    """

    def __init__(self,
                 added: datetime,
                 started: Optional[datetime],
                 running_time: int,
                 paused_time: int = 0):
        """!
        @param added The date and time when the job was first added in the database.
        @param started The date and time when the job was first started, or None if the job has never been started.
        @param running_time The amount of time that the job has been running for, in seconds.
        @param paused_time The amount of time that the job has been paused for, in seconds
        """
        if running_time < 0:
            raise ValueError("Running time must be positive integer!")
        if paused_time < 0:
            raise ValueError("Paused time must be a positive integer!")
        if started is not None and added > started:
            raise ValueError("Cannot start job before adding it, added must be smaller than started!")

        self._added = added
        self._started = started
        self._running_time = running_time
        self._paused_time = paused_time

    def __eq__(self, o: object) -> bool:
        if isinstance(o, JobRuntimeStatistics):
            return self.time_started == o.time_started and self.time_started == o.time_started \
                and self.running_time == o.running_time and self.paused_time == o.paused_time
        return False

    @property
    def time_added(self) -> datetime:
        """!
        @return The date and time when the job entry was first added.
        """
        return self._added

    @time_added.setter
    def time_added(self, added: datetime) -> None:
        self._added = added

    @property
    def time_started(self) -> datetime:
        """!
        @return The date and time when the job was started for the first time,
           or None if the job has not been started yet.
        """
        return self._started

    @time_started.setter
    def time_started(self, started: datetime) -> None:
        self._started = started

    @property
    def running_time(self) -> int:
        """!
        @return The amount of time that the job has been running for, in seconds.
        """
        return self._running_time

    @running_time.setter
    def running_time(self, running_time: int) -> None:
        self._running_time = running_time

    @property
    def paused_time(self) -> int:
        """!
        @return The amount of time that the job has been paused for, in seconds.
        """
        return self._paused_time

    @paused_time.setter
    def paused_time(self, paused_time: int) -> None:
        self._paused_time = paused_time


class DatabaseJobEntry:
    """
    A job entry in the database.
    """

    def __init__(self,
                 job: Job,
                 stats: JobRuntimeStatistics,
                 machine: Optional[WorkMachine]):
        """!
        Construct a new database job entry.

        @param job The job stored in the database entry.
        @param stats The statistics about the job runtime stored in the database.
        @param machine The work machine this job has been assigned to, if any.
        """
        self._job = job
        self._statistics = stats
        self._machine = machine

    def __eq__(self, o: object) -> bool:
        if isinstance(o, DatabaseJobEntry):
            return self.job == o.job and self.assigned_machine == o.assigned_machine and self.statistics == o.statistics
        return False

    @property
    def job(self) -> Job:
        """!
        @return The job stored in this database entry.
        """
        return self._job

    @job.setter
    def job(self, job: Job) -> None:
        self._job = job

    @property
    def statistics(self) -> JobRuntimeStatistics:
        """!
        @return The statistics about the job stored in the database.
        """
        return self._statistics

    @property
    def assigned_machine(self) -> WorkMachine:
        """!
        @return The assigned work machine of the job, or None if the job is not currently running on any machine.
        """
        return self._machine

    @assigned_machine.setter
    def assigned_machine(self, machine: WorkMachine) -> None:
        self._machine = machine
