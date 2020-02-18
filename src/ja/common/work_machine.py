from typing import Dict, cast

from ja.common.message.base import Serializable


class ResourceAllocation(Serializable):
    """
    Represents a group of resources on a work machine.
    """

    def __init__(self, cpu_threads: int, memory: int, swap: int):
        """!
        Create the ResourceAllocation object.

        @param cpu_threads The amount of CPU threads.
        @param memory The amount of RAM, in MB.
        @param swap The amount of swap space, in MB.
        """
        self._cpu_threads = cpu_threads
        self._memory = memory
        self._swap = swap

    @property
    def cpu_threads(self) -> int:
        """!
        @return The allocated CPU threads.
        """
        return self._cpu_threads

    @property
    def memory(self) -> int:
        """!
        @return The allocated RAM in MB.
        """
        return self._memory

    @property
    def swap(self) -> int:
        """!
        @return The allocated swap space in MB.
        """
        return self._swap

    def is_negative(self) -> bool:
        """
        @returns bool indicating if any of the attributes is negative
        """
        ret: bool = self._cpu_threads < 0 or self._memory < 0 or self._swap < 0
        return ret

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ResourceAllocation):
            return self._cpu_threads == other.cpu_threads and self._memory == other.memory and self._swap == other.swap
        else:
            return False

    def __sub__(self, other: "ResourceAllocation") -> "ResourceAllocation":
        cpu_threads: int = self._cpu_threads - other.cpu_threads
        memory: int = self._memory - other.memory
        swap: int = self._swap - other.swap

        return ResourceAllocation(cpu_threads, memory, swap)

    def __add__(self, other: "ResourceAllocation") -> "ResourceAllocation":
        cpu_threads: int = self._cpu_threads + other.cpu_threads
        memory: int = self._memory + other.memory
        swap: int = self._swap + other.swap

        return ResourceAllocation(cpu_threads, memory, swap)

    def __isub__(self, other: "ResourceAllocation") -> "ResourceAllocation":
        self._cpu_threads -= other.cpu_threads
        self._memory -= other.memory
        self._swap -= other.swap

        return self

    def __iadd__(self, other: "ResourceAllocation") -> "ResourceAllocation":
        self._cpu_threads += other.cpu_threads
        self._memory += other.memory
        self._swap += other.swap

        return self

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["cpu_threads"] = self._cpu_threads
        _dict["memory"] = self._memory
        _dict["swap"] = self._swap

        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ResourceAllocation":
        _cpu_threads: int = cast(int, property_dict["cpu_threads"])
        _memory: int = cast(int, property_dict["memory"])
        _swap: int = cast(int, property_dict["swap"])

        return ResourceAllocation(_cpu_threads, _memory, _swap)
