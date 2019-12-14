from ja.common.work_machine import ResourceAllocation


class RunningWorkMachineResources:
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
        @return The maximum resources available on the work machine.
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


class WorkMachineConnectionDetails:
    """
    A collection of the data needed to communicate with a work machine.
    """
    # TODO: this class is incomplete


class WorkMachine:
    """
    Represents the data stored about a work machine in the database.
    Each work machine is uniquely determined by its IP address.
    (XXX: is the above ok?)
    """
    def __init__(self,
                 is_online: bool = False,
                 resources: RunningWorkMachineResources = None,
                 connection: WorkMachineConnectionDetails = None):
        """!
        Construct a new work machine object.
        If the work machine is not online, then only statistics about it are
        stored. Otherwise, the work machine also tracks available resources
        and connection details.

        @param is_online Whether the work machine is online.
        @param resources The available resources on the work machine.
        @param connection The connection informatino about the work machine.
        """

    @property
    def online(self) -> bool:
        """!
        @return True if the work machine is online and connected to the server,
          False otherwise.
        """

    @property
    def resources(self) -> RunningWorkMachineResources:
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
