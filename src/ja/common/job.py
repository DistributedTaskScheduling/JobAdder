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
    @param scheduling_constraints The docker constraints of the job.
    @param docker_context The docker context of the job.
    @param label The label set by the user for the job.
    """
    def __init__(self,
                 owner_id: int,
                 email: str,
                 scheduling_constraints: JobSchedulingConstraints,
                 docker_context: IDockerContext,
                 docker_constraints: DockerConstraints,
                 label: str = None):
        self._uid: str = None
        self._status: JobStatus = JobStatus.NEW
        self._owner_id = owner_id
        self._email = email
        self._scheduling_constraints = scheduling_constraints
        self._docker_context = docker_context
        self._docker_constraints = docker_constraints
        self._label = label

    @property
    def uid(self) -> str:
        """!
        Get the job unique identifier used to create the job.
        If the job has not been queued yet, it has no UID.
        """
        return self._uid

    @uid.setter
    def uid(self, value: str) -> None:
        """!
        Set the job UID.
        If the job has an UID already set, this results in a RuntimeError.

        @param value The new job UID.
        """
        self._uid = value

    @property
    def owner_id(self) -> int:
        """!
        @return The id of the user who owns the job.
        """
        return self._owner_id

    @property
    def email(self) -> str:
        """!
        @return The email of the user who owns the job, or None if no email was specified.
        """
        return self._email

    @property
    def scheduling_constraints(self) -> JobSchedulingConstraints:
        """!
        @return The scheduling constraints of the job.
        """
        return self._scheduling_constraints

    @property
    def docker_context(self) -> IDockerContext:
        """!
        @return The docker context of the job.
        """
        return self._docker_context

    @property
    def docker_constraints(self) -> DockerConstraints:
        """!
        @return The docker constraints of the job.
        """
        return self._docker_constraints

    @property
    def status(self) -> JobStatus:
        """!
        @return The current job status.
        """
        return self._status

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
        self._status = new_status

    @property
    def label(self) -> str:
        """!
        @return: The label set by the user for this job.
        """
        return self._label

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["uid"] = self.uid
        _dict["owner_id"] = self.owner_id
        _dict["email"] = self.email
        _dict["scheduling_constraints"] = self.scheduling_constraints.to_dict()
        _dict["docker_context"] = self.docker_context.to_dict()
        _dict["docker_constraints"] = self.docker_constraints.to_dict()
        _dict["status"] = self.status
        _dict["label"] = self.label
        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "Job":
        _uid: str = cls._get_str_from_dict(property_dict=property_dict, key="uid", mandatory=False)
        _owner_id: int = cls._get_int_from_dict(property_dict=property_dict, key="uid")
        _email: str = cls._get_str_from_dict(property_dict=property_dict, key="email")

        _scheduling_constraints = JobSchedulingConstraints.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="scheduling_constraints")
        )

        _docker_context = IDockerContext.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="docker_context")
        )

        _docker_constraints = DockerConstraints.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="docker_constraints")
        )

        _status = JobStatus(cls._get_from_dict(property_dict=property_dict, key="status"))

        _label = cls._get_str_from_dict(property_dict=property_dict, key="label", mandatory=False)

        cls._assert_all_properties_used(property_dict)

        _job = Job(
            owner_id=_owner_id, email=_email, scheduling_constraints=_scheduling_constraints,
            docker_context=_docker_context, docker_constraints=_docker_constraints, label=_label
        )
        _job.uid = _uid
        _job.status = _status
        return _job
