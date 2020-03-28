from ja.common.job import JobStatus
from ja.server.database.database import ServerDatabase
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase
from typing import Dict


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
        self._proxy_factory = proxy_factory
        self._previous_statuses: Dict[str, JobStatus] = dict()

    def set_distribution(self, job_distribution: JobDistribution) -> None:
        """!
        Distributes the newly added jobs to the work machines.
        and potentially pauses jobs that need to be paused.

        @param job_distribution the new job distribution.
        """
        new_statuses: Dict[str, JobStatus] = dict()
        for job_entry in job_distribution:
            job = job_entry.job
            work_machine = job_entry.assigned_machine
            previous_status = self._previous_statuses.get(job.uid, None)
            if (previous_status is None or job.status != previous_status) and work_machine is not None:
                proxy = self._proxy_factory.get_proxy(work_machine)
                if job.status == JobStatus.RUNNING:
                    if previous_status is None or previous_status == JobStatus.QUEUED:
                        proxy.dispatch_job(job)
                    elif previous_status == JobStatus.PAUSED:
                        proxy.resume_job(job.uid)
                    new_statuses[job.uid] = job.status
                elif job.status == JobStatus.CANCELLED:
                    proxy.cancel_job(job.uid)  # Do not add job back to self._previous_statuses
                elif job.status == JobStatus.PAUSED:
                    proxy.pause_job(job.uid)
                    new_statuses[job.uid] = job.status
                elif job.status == JobStatus.QUEUED:
                    new_statuses[job.uid] = job.status
                else:
                    raise ValueError("Received unexpected state %s for job with UID %s." % (job.status.name, job.uid))
        self._previous_statuses = new_statuses
