from enum import Enum

from ja.common.work_machine import ResourceAllocation


class WorkMachineResources:
    """
    Represents the resources of a work machine which is currently connected to
    the central server.

    In addition to the available resources, a running work machine also tracks
    how much of its resources are currently used.
    """
    def __init__(self, total_resources: ResourceAllocation):
        """!
        Initialize the RunningWorkMachineResources object. In the beginning,
        all resources are marked as free.

        @param total_resources The total amount of available resources.
        """

    @property
    def total_resources(self) -> ResourceAllocation:
        """!
        @return The total amount resources available on the work machine (both
        free and allocated resources).
        """

    @property
    def free_resources(self) -> ResourceAllocation:
        """!
        @return The currently available resources on the work machine.
        """

    def allocate(self,
                 allocation: ResourceAllocation,
                 test_only: bool = False) -> bool:
        """!
        Add the requested resources to the list of already allocated resources.
        These resources will not be marked as free afterwards.

        @param allocation The CPU, memory and swap space to allocate.
        @param test_only If set to True, only the availability of enough
          resources will be checked, but the resources will not be actually
          allocated.
        @return True if the allocation or the test was successful, False
          otherwise.
        """

    def deallocate(self,
                   allocation: ResourceAllocation) -> bool:
        """!
        Mark the given resources as free.

        @param allocation The amount of resources to free.
        @return True if there are at least as @allocation resources allocated,
          False if the amount of resources to be freed exceeds the total amount
          of allocated resources.
        """


class WorkMachineConnectionDetails:
    """
    A collection of the data needed to communicate with a work machine.
    """
    # TODO: this class is incomplete


class WorkMachineState(Enum):
    ONLINE = 0
    RETIRED = 10
    OFFLINE = 20


class WorkMachine:
    """
    Represents the data stored about a work machine in the database.
    Each work machine is uniquely determined by its UID.
    """
    def __init__(self,
                 uid: str,
                 state: WorkMachineState = WorkMachineState.OFFLINE,
                 resources: WorkMachineResources = None,
                 connection: WorkMachineConnectionDetails = None):
        """!
        Construct a new work machine object.
        If the work machine is not online, then only statistics about it are
        stored. Otherwise, the work machine also tracks available resources
        and connection details.

        @param uid The unique ID of the machine.
        @param state Whether the work machine is online, retired, or offline.
        @param resources The available resources on the work machine.
        @param connection The connection information about the work machine.
        """

    @property
    def uid(self) -> str:
        """!
        @return The UID of the work machine.
        """

    @property
    def state(self) -> WorkMachineState:
        """!
        @return: Whether the work machine is online, retired, or offline.
        """

    @property
    def resources(self) -> WorkMachineResources:
        """!
        @return The resources of the work machine, if it is online,
          otherwise None.
        """

    @property
    def connection_details(self) -> WorkMachineConnectionDetails:
        """!
        @return The connection details of the work machine, if it is online,
          otherwise None.
        """
