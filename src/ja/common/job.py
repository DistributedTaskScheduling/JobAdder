"""
This module contains the definition of the Job class and related structures.
"""
from typing import List, Dict, Optional
from enum import Enum
from ja.common.docker_context import DockerConstraints, IDockerContext, DockerContext
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
    CANCELLED = 5
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
                 is_preemptible: bool,
                 special_resources: List[str]):
        self._priority = priority
        self._is_preemptible = is_preemptible
        self._special_resources = special_resources

    def __eq__(self, other: object) -> bool:
        if isinstance(other, JobSchedulingConstraints):
            return self.priority == other.priority \
                and self.is_preemptible == other.is_preemptible \
                and self.special_resources == other.special_resources
        else:
            return False

    @property
    def priority(self) -> JobPriority:
        """!
        @return The priority of the job.
        """
        return self._priority

    @property
    def is_preemptible(self) -> bool:
        """!
        @return Whether the job can be preempted.
        """
        return self._is_preemptible

    @property
    def special_resources(self) -> List[str]:
        """!
        @return A list of special resources used by the job.
        """
        return self._special_resources

    def to_dict(self) -> Dict[str, object]:
        return_dict: Dict[str, object] = dict()
        return_dict["priority"] = self.priority
        return_dict["is_preemptible"] = self.is_preemptible
        return_dict["special_resources"] = self.special_resources
        return return_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "JobSchedulingConstraints":
        priority = JobPriority(cls._get_from_dict(property_dict=property_dict, key="priority"))
        is_preemptible = cls._get_bool_from_dict(property_dict=property_dict, key="is_preemptible")
        special_resources = cls._get_str_list_from_dict(property_dict=property_dict, key="special_resources")

        cls._assert_all_properties_used(property_dict)

        return JobSchedulingConstraints(
            priority=priority, is_preemptible=is_preemptible, special_resources=special_resources)


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
                 docker_context: DockerContext,
                 docker_constraints: DockerConstraints,
                 label: str = None,
                 status: JobStatus = JobStatus.NEW):
        self._owner_id = owner_id
        self._email = email
        self._scheduling_constraints = scheduling_constraints
        self._docker_context = docker_context
        self._docker_constraints = docker_constraints
        self._label = label
        self._uid: Optional[str] = None
        self._status = status

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Job):
            return self.uid == other.uid \
                and self.status == other.status \
                and self.owner_id == other.owner_id \
                and self.email == other.email \
                and self.scheduling_constraints == other.scheduling_constraints \
                and self.docker_context == other.docker_context \
                and self.docker_constraints == other.docker_constraints \
                and self.label == other.label
        else:
            return False

    def __str__(self) -> str:
        return str(self.to_dict)

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

    @owner_id.setter
    def owner_id(self, owner_id: int) -> None:
        self._owner_id = owner_id

    @property
    def email(self) -> str:
        """!
        @return The email of the user who owns the job, or None if no email was specified.
        """
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        self._email = email

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
        QUEUED -> CANCELLED | RUNNING
        RUNNING -> PAUSED | DONE | CANCELLED | CRASHED
        PAUSED -> CANCELLED | RUNNING

        If the transition requested is not allowed, or if the job has not
        been assigned an UID, a RuntimeError will be raised.

        @param new_status The new status of the job.
        """
        if self._status == JobStatus.NEW:
            transition_legal = new_status == JobStatus.QUEUED
        elif self._status == JobStatus.QUEUED:
            transition_legal = new_status in [JobStatus.CANCELLED, JobStatus.RUNNING]
        elif self._status == JobStatus.RUNNING:
            transition_legal = new_status in [JobStatus.PAUSED, JobStatus.DONE, JobStatus.CANCELLED, JobStatus.CRASHED]
        elif self._status == JobStatus.PAUSED:
            transition_legal = new_status in [JobStatus.CANCELLED, JobStatus.RUNNING]
        else:
            transition_legal = False
        if transition_legal:
            self._status = new_status
        else:
            raise ValueError("Illegal job status transition: %s -> %s" % (self._status.name, new_status.name))

    @property
    def label(self) -> str:
        """!
        @return: The label set by the user for this job.
        """
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        self._label = label

    def to_dict(self) -> Dict[str, object]:
        return_dict: Dict[str, object] = dict()
        return_dict["uid"] = self.uid
        return_dict["owner_id"] = self.owner_id
        return_dict["email"] = self.email
        return_dict["scheduling_constraints"] = self.scheduling_constraints.to_dict()
        return_dict["docker_context"] = self.docker_context.to_dict()
        return_dict["docker_constraints"] = self.docker_constraints.to_dict()
        return_dict["status"] = self.status
        return_dict["label"] = self.label
        return return_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "Job":
        uid = cls._get_str_from_dict(property_dict=property_dict, key="uid", mandatory=False)
        owner_id = cls._get_int_from_dict(property_dict=property_dict, key="owner_id")
        email = cls._get_str_from_dict(property_dict=property_dict, key="email", mandatory=False)

        scheduling_constraints = JobSchedulingConstraints.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="scheduling_constraints")
        )

        docker_context: DockerContext = DockerContext.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="docker_context")
        )

        docker_constraints = DockerConstraints.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="docker_constraints")
        )

        status = JobStatus(cls._get_from_dict(property_dict=property_dict, key="status"))

        label = cls._get_str_from_dict(property_dict=property_dict, key="label", mandatory=False)

        cls._assert_all_properties_used(property_dict)

        job = Job(
            owner_id=owner_id, email=email, scheduling_constraints=scheduling_constraints,
            docker_context=docker_context, docker_constraints=docker_constraints, label=label
        )
        job.uid = uid
        job._status = status  # Bypass check whether transition from JobStatus.NEW is legal
        return job
