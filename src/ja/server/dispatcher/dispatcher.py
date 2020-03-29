from ja.common.job import JobStatus
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase
from typing import Dict, List
from paramiko.ssh_exception import SSHException  # type: ignore

import logging
logger = logging.getLogger(__name__)

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
        self._lost_work_machines: List[WorkMachine] = []

    _job_status_order = [JobStatus.QUEUED, JobStatus.CANCELLED, JobStatus.PAUSED, JobStatus.RUNNING]

    @staticmethod
    def _sort_key_function(job: DatabaseJobEntry) -> int:
        """
        Returns keys so that first we cancel jobs, then we pause jobs, and finally start new jobs.
        """
        if job.job.status not in Dispatcher._job_status_order:
            raise ValueError("Received unexpected state %s for job with UID %s." % (job.job.status.name, job.job.uid))

        return Dispatcher._job_status_order.index(job.job.status)

    def set_distribution(self, job_distribution: JobDistribution) -> List[WorkMachine]:
        """!
        Distributes the newly added jobs to the work machines.
        and potentially pauses jobs that need to be paused.

        @param job_distribution the new job distribution.
        @return a list of all work machines that the server has lost connection to.
        """
        logger.debug("Dispatching jobs")
        new_statuses: Dict[str, JobStatus] = dict()

        self._lost_work_machines.clear()
        for job_entry in sorted(job_distribution, key=self._sort_key_function):
            job = job_entry.job
            if job.status == JobStatus.QUEUED:
                logger.debug("Job %s queued." % job.uid)
                continue

            work_machine = job_entry.assigned_machine
            proxy = self._proxy_factory.get_proxy(work_machine)

            logger.debug("Job %s with status %s on %s." % (job.uid, job.status.name, work_machine.uid))
            previous_status = self._previous_statuses.get(job.uid, None)
            if previous_status is None or job.status != previous_status:
                try:
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
                    else:
                        raise ValueError("Received unexpected state %s for job with UID %s." %
                                         (job.status.name, job.uid))
                except SSHException:
                    self._timeout(job_entry)
            else:
                # If the job status hasn't changed, try to ping the machine to make sure it is not dead.
                try:
                    proxy.check_connection()
                    new_statuses[job.uid] = job.status
                except SSHException:
                    self._timeout(job_entry)

        self._previous_statuses = new_statuses
        return self._lost_work_machines

    def _timeout(self, entry: DatabaseJobEntry) -> None:
        if any(machine.uid == entry.assigned_machine.uid for machine in self._lost_work_machines):
            return

        logger.error("Lost connection to Work machine with id %s." % entry.assigned_machine.uid)
        self._lost_work_machines.append(entry.assigned_machine)
