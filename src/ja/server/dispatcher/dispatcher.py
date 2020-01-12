from ja.common.job import Job
from ja.server.proxy.proxy import WorkerProxy
from typing import List
from ja.server.database.database import ServerDatabase


JobDistribution = ServerDatabase.JobDistribution


class Dispatcher:
    """
    Represents the mediator between the Scheduler and the work machines.
    """

    def __init__(self, worker_proxies: List[WorkerProxy]):
        """!
        Constructor for the dispatcher class.
        @param worker_proxies proxies of the work machines.
        """

    def set_distribution(self, job_distribution: JobDistribution) -> None:
        """!
        Distributes the newly added jobs to the work machines.
        and potentially pauses jobs that need to be paused.

        @param jobs list of the new job distribution.
        """

    def _get_changed_jobs(self, jobs: List[Job]) -> List[Job]:
        """!
        @return list of the jobs whose state has been changed.
        """

    def _reset(self) -> None:
        """!
        Dispatches the added jobs, pauses the paused jobs and cancels the cancelled jobs.
        """

    @property
    def woker_proxies(self) -> List[WorkerProxy]:
        """!
        @return work machine proxies.
        """
