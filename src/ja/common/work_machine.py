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

    @property
    def cpu_threads(self) -> int:
        """!
        @return The allocated CPU threads.
        """

    @property
    def memory(self) -> int:
        """!
        @return The allocated RAM in MB.
        """

    @property
    def swap(self) -> int:
        """!
        @return The allocated swap space in MB.
        """
