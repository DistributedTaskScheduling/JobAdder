"""
This file contains several classes which represent the data stored in the
database.
"""
from datetime import datetime
from ja.common.job import Job
from ja.common.workmachine import ResourceAllocation


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


class JobRuntimeStatistics:
    """
    A collection of statistics about the job's running time, queued time, etc.
    """
    def __init__(self,
                 added: datetime,
                 started: datetime,
                 running_time: int):
        """!
        @param added The date and time when the job was first added in the
          database.
        @param started The date and time when the job was first started, or
          None if the job has never been started.
        @param running_time The length of the time when the job has been
          running, in seconds.
        """

    @property
    def time_added(self) -> datetime:
        """!
        @return The date and time when the job entry was first added.
        """

    @property
    def time_started(self) -> datetime:
        """!
        @return The date and time when the job was started for the first time,
           or None if the job has not been started yet.
        """

    @property
    def running_time(self) -> int:
        """!
        @return The length of time during which the job has been running, in
           seconds.
        """


class DatabaseJobEntry:
    """
    A job entry in the database.
    """
    def __init__(self,
                 job: Job,
                 stats: JobRuntimeStatistics,
                 machine: WorkMachine):
        """!
        Construct a new database job entry.

        @param job The job stored in the database entry.
        @param stats The statistics about the job runtime stored in the
          database.
        @param machine The work machine this job has been assigned to, if any.
        """

    @property
    def job(self) -> Job:
        """!
        @return The job stored in this database entry.
        """

    @property
    def statistics(self) -> JobRuntimeStatistics:
        """!
        @return The statistics about the job stored in the database.
        """

    @property
    def assigned_machine(self) -> WorkMachine:
        """!
        @return The assigned work machine of the job, or None if the job is not
          currently running on any machine.
        """
