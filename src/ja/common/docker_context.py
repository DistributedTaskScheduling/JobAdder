"""
Contains definitions of the various Docker-related attributes of a job.
These include, but are not limited to, mount points, program environment
and hardware constraints.
"""
from abc import ABC, abstractmethod
from typing import List


class MountPoint:
    """!
    A mount point consists of:
    1. A directory to be mounted(@source_path).
    2. The target path in the Docker container where the directory needs to be
    mounted(@mount_path).
    """
    def __init__(self, source_path: str, mount_path: str):
        """!
        Initializes a new mount point.
        @param source_path The host directory to be mounted.
        @param mount_path The target path in the container to mount at.
        """

    @property
    def source_path(self) -> str:
        """!
        @return The directory to be mounted.
        """

    @property
    def mount_path(self) -> str:
        """!
        @return The path where the directory should be mounted.
        """


class IDockerContext(ABC):
    """
    A docker context consists of the necessary data to build a docker image to
    run a job in.
    """

    @abstractmethod
    def get_dockerfile_source(self) -> str:
        """!
        @return The string contents of a Dockerfile which can be used to build
        the docker image.
        """

    @abstractmethod
    def get_mount_points(self) -> List[MountPoint]:
        """!
        @return A list of all mount points for the job.
        """


class DockerConstraints:
    """
    A list of constraints of the docker container.
    """
    def __init__(self, cpu_threads: int = -1, memory: int = 1):
        """!
        Create a new set of Docker constraints.
        @param cpu_threads Initial value of @cpu_threads.
        @param memory The value of @memory.
        """

    @property
    def cpu_threads(self) -> int:
        """!
        @return The maximum number of CPU threads the docker container can use.
        -1 means that the amount of threads is not set, in which case the
        number of threads will be determined when scheduling the job.
        """

    @cpu_threads.setter
    def cpu_threads(self, count_threads: int) -> None:
        """!
        Set the number of CPU threads.
        If the number of cpu threads is already set(i.e it is not equal to -1),
        this will raise a RuntimeError.
        """

    @property
    def memory(self) -> int:
        """!
        @return The maximum amount of RAM in MB to allocate for this container.
        """
