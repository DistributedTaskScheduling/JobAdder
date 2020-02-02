from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase
from typing import List


JobDistribution = ServerDatabase.JobDistribution


class Dispatcher:
    """
    Represents the mediator between the Scheduler and the work machines.
    """

    def __init__(self, proxy_factory: WorkerProxyFactoryBase):
        """!
        Constructor for the dispatcher class.
        @param proxy_factory The proxy factory to use to create WorkerProxies
        """

    def set_distribution(self, job_distribution: JobDistribution) -> None:
        """!
        Distributes the newly added jobs to the work machines.
        and potentially pauses jobs that need to be paused.

        @param job_distribution the new job distribution.
        """

    def _get_changed_jobs(self, jobs: List[Job]) -> List[Job]:
        """!
        @return list of the jobs whose state has been changed.
        """

    def _reset(self) -> None:
        """!
        Dispatches the added jobs, pauses the paused jobs and cancels the cancelled jobs.
        """
