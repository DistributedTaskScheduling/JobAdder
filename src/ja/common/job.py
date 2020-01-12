"""
This module contains the definition of the Job class and related structures.
"""
from typing import List, Dict
from enum import Enum
from ja.common.docker_context import DockerConstraints, IDockerContext
from ja.common.message.base import Serializable


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


class JobSchedulingConstraints(Serializable):
    """
    JobConstraints is a collection of job properties which affect how it is
    scheduled.
    """
    def __init__(self,
                 priority: JobPriority,
                 is_preemtible: bool,
                 special_resources: List[str]):
        pass

    @property
    def priority(self) -> JobPriority:
        """!
        @return The priority of the job.
        """

    @property
    def is_preemptible(self) -> bool:
        """!
        @return Whether the job can be preempted.
        """

    @property
    def get_special_resources(self) -> List[str]:
        """!
        @return A list of special resources used by the job.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobSchedulingConstraints":
        pass


class Job(Serializable):
    """!
    Represents a job with all of its attributes.
    @param owner_id The unix user id of the user who owns this job.
    @param email The email of the user who created the job, or None.
    @param ctx The docker context of the job.
    @param constraints The docker constraints of the job.
    @param label The label set by the user for the job.
    """
    def __init__(self,
                 owner_id: int,
                 email: str,
                 constraints: JobSchedulingConstraints,
                 ctx: IDockerContext,
                 docker_constraints: DockerConstraints,
                 label: str = None):
        pass

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
    def label(self) -> str:
        """!
        @return: The label set by the user for this job.
        """

    @property
    def owner_id(self) -> int:
        """!
        @return The id of the user who owns the job.
        """

    @property
    def email(self) -> str:
        """!
        @return The email of the user who owns the job, or None if no email was specified.
        """

    @property
    def scheduling_constraints(self) -> JobSchedulingConstraints:
        """!
        @return The scheduling constraints of the job.
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

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "Job":
        pass
