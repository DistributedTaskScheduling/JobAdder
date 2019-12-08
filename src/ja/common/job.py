"""
This module contains the definition of the Job class and related structures.
"""
from enum import Enum
from ja.common.docker_context import DockerConstraints, IDockerContext


class JobStatus(Enum):
    """
    Represents the status of a job.
    """
    NEW = 0
    QUEUED = 1
    RUNNING = 2
    PAUSED = 3
    DONE = 4
    KILLED = 5
    CRASHED = 6


class JobPriority(Enum):
    """
    Represents the base priority of a job.
    """
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3


class Job:
    """!
    Represents a job with all of its attributes.
    @param owner_id The unix user id of the user who owns this job.
    @param priority The priority of the job.
    @param ctx The docker context of the job.
    @param constraints The docker constraints of the job.
    """
    def __init__(self,
                 owner_id: int,
                 priority: JobPriority,
                 ctx: IDockerContext,
                 constraints: DockerConstraints):
        self._uid = None
        self._status = JobStatus.NEW
        self._priority = priority
        self._ownerid = owner_id
        self._ctx = ctx
        self._constraints = constraints

    @property
    def uid(self) -> str:
        """!
        Get the job unique identifier used to create the job.
        If the job has not been queued yet, it has no UID.
        """

    @uid.setter
    def uid(self, value: str) -> None:
        """!
        Set the job UID.
        If the job has an UID already set, this results in a RuntimeError.

        @param value The new job UID.
        """

    @property
    def owner_id(self) -> int:
        """!
        @return The id of the user who owns the job.
        """

    @property
    def priority(self) -> JobPriority:
        """!
        @return The job priority.
        """

    @property
    def status(self) -> JobStatus:
        """!
        @return The current job status.
        """

    @status.setter
    def status(self, new_status: JobStatus) -> None:
        """!
        Set the job status.
        The following transitions are allowed:
        NEW -> QUEUED
        QUEUED -> KILLED | RUNNING
        RUNNING -> PAUSED | DONE | KILLED | CRASHED
        PAUSED -> KILLED | RUNNING

        If the transition requested is not allowed, or if the job has not
        been assigned an UID, a RuntimeError will be raised.

        @param new_status The new status of the job.
        """

    @property
    def docker_context(self) -> IDockerContext:
        """!
        @return The docker context of the job.
        """

    @property
    def docker_constraints(self) -> DockerConstraints:
        """!
        @return The docker constraints of the job.
        """
