"""
Contains definitions of the various Docker-related attributes of a job.
These include, but are not limited to, mount points, program environment
and hardware constraints.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, cast
from ja.common.message.base import Serializable


class MountPoint(Serializable):
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
        self._source_path = source_path
        self._mount_path = mount_path

    @property
    def source_path(self) -> str:
        """!
        @return The directory to be mounted.
        """
        return self._source_path

    @property
    def mount_path(self) -> str:
        """!
        @return The path where the directory should be mounted.
        """
        return self._mount_path

    def to_dict(self) -> Dict[str, object]:
        return {"source_path": self.source_path, "mount_path": self.mount_path}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "MountPoint":
        _source_path = cls._get_str_from_dict(property_dict=property_dict, key="source_path")
        _mount_path = cls._get_str_from_dict(property_dict=property_dict, key="mount_path")
        cls._assert_all_properties_used(property_dict)
        return MountPoint(source_path=_source_path, mount_path=_mount_path)


class IDockerContext(Serializable, ABC):
    """
    A docker context consists of the necessary data to build a docker image to
    run a job in.
    """

    @property
    @abstractmethod
    def dockerfile_source(self) -> str:
        """!
        @return The string contents of a Dockerfile which can be used to build
        the docker image.
        """

    @property
    @abstractmethod
    def mount_points(self) -> List[MountPoint]:
        """!
        @return A list of all mount points for the job.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "IDockerContext":
        pass


class DockerContext(IDockerContext):
    """
    An implementation of the IDockerContext interface
    """
    def __init__(self, dockerfile_source: str, mount_points: List[MountPoint]):
        """
        @param dockerfile_source: The string contents of a Dockerfile which can be used to build the docker image.
        @param mount_points: A list of all mount points for the job.
        """
        self._dockerfile_source = dockerfile_source
        self._mount_points = mount_points

    @property
    def dockerfile_source(self) -> str:
        return self._dockerfile_source

    @property
    def mount_points(self) -> List[MountPoint]:
        return self._mount_points

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["dockerfile_source"] = self.dockerfile_source
        _dict["mount_points"] = [_mount_point.to_dict() for _mount_point in self.mount_points]
        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "IDockerContext":
        _dockerfile_source = cls._get_str_from_dict(property_dict=property_dict, key="dockerfile_source")

        _property: object = cls._get_from_dict(property_dict=property_dict, key="mount_points")
        if not isinstance(_property, list):
            cls._raise_error_wrong_type(
                key="mount_points", expected_type="List[MountPoint]",
                actual_type=_property.__class__.__name__
            )
        _object_list = cast(List[object], _property)
        _mount_point_list: List[MountPoint] = []
        for _object in _object_list:
            if not isinstance(_object, dict):
                cls._raise_error_wrong_type(
                    key="mount_points", expected_type="List[MountPoint]",
                    actual_type="List[object]"
                )
                _mount_point_list.append(MountPoint.from_dict(
                    cast(Dict[str, object], _object)
                ))
        cls._assert_all_properties_used(property_dict)
        return DockerContext(dockerfile_source=_dockerfile_source, mount_points=_mount_point_list)


class DockerConstraints(Serializable):
    """
    A list of constraints of the docker container.
    """
    def __init__(self, cpu_threads: int = -1, memory: int = 1):
        """!
        Create a new set of Docker constraints.
        @param cpu_threads Initial value of @cpu_threads.
        @param memory The value of @memory.
        """
        self._cpu_threads = -1
        self.cpu_threads = cpu_threads
        if memory < 1:
            raise ValueError("Cannot set memory to %s because this value is < 1." % memory)
        self._memory = memory

    @property
    def cpu_threads(self) -> int:
        """!
        @return The maximum number of CPU threads the docker container can use.
        -1 means that the amount of threads is not set, in which case the
        number of threads will be determined when scheduling the job.
        """
        return self._cpu_threads

    @cpu_threads.setter
    def cpu_threads(self, count_threads: int) -> None:
        """!
        Set the number of CPU threads.
        If the number of cpu threads is already set(i.e it is not equal to -1),
        this will raise a RuntimeError.
        """
        if self._cpu_threads != -1:
            raise RuntimeError("cpu_threads can only be set once.")
        if count_threads < 1:
            raise ValueError("Cannot set cpu_threads to %s because this value is < 1." % count_threads)
        self._cpu_threads = count_threads

    @property
    def memory(self) -> int:
        """!
        @return The maximum amount of RAM in MB to allocate for this container.
        """
        return self._memory

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["cpu_threads"] = self.cpu_threads
        _dict["memory"] = self.memory
        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "DockerConstraints":
        _cpu_threads = cls._get_int_from_dict(property_dict=property_dict, key="cpu_threads")
        _memory = cls._get_int_from_dict(property_dict=property_dict, key="memory")
        cls._assert_all_properties_used(property_dict)
        return DockerConstraints(cpu_threads=_cpu_threads, memory=_memory)
