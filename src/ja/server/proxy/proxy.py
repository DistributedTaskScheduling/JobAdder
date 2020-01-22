from abc import ABC, abstractmethod

from ja.common.proxy.proxy import ContinuousProxy
from ja.common.proxy.ssh import SSHConfig
from ja.common.message.worker import WorkerResponse
from ja.common.job import Job


class IWorkerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the worker client used on the central server.
    """
    DISPATCH_JOB_SUCCESS = "Successfully dispatched job with UID %s to worker with UID %s."
    DISPATCH_JOB_DUPLICATE = "Could not dispatch job with UID %s because worker with UID %s already has this job."
    CANCEL_JOB_SUCCESS = "Successfully canceled job with UID %s on worker with UID %s."
    CANCEL_JOB_UNKNOWN_JOB = "Could not cancel job with UID %s because worker with UID %s does not have this job."
    PAUSE_JOB_SUCCESS = "Successfully paused job with UID %s on worker with UID %s."
    PAUSE_JOB_NOT_RUNNING = "Could not pause job with UID %s on worker with UID %s because the job is not running."
    PAUSE_JOB_UNKNOWN_JOB = "Could not pause job with UID %s because worker with UID %s does not have this job."
    RESUME_JOB_SUCCESS = "Successfully resumed job with UID %s on worker with UID %s."
    RESUME_JOB_NOT_PAUSED = "Could not resume job with UID %s on worker with UID %s because the job is not paused."
    RESUME_JOB_UNKNOWN_JOB = "Could not resume job with UID %s because worker with UID %s does not have this job."

    def __init__(self, uid: str, ssh_config: SSHConfig):
        """!
        @param uid: The UID of the worker represented by this proxy.
        @param ssh_config: Config for paramiko.
        """

    @property
    @abstractmethod
    def uid(self) -> str:
        """!
        @return: The UID of the worker represented by this proxy.
        """

    @abstractmethod
    def dispatch_job(self, job: Job) -> WorkerResponse:
        """!
        @param job: A Job to be dispatched to the worker client.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def cancel_job(self, uid: str) -> WorkerResponse:
        """!
        @param uid: uid of the Job to be cancelled.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def pause_job(self, uid: str) -> WorkerResponse:
        """!
        @param uid: uid of the Job to be paused.
        @return: The Response from the worker client.
        """

    @abstractmethod
    def resume_job(self, uid: str) -> WorkerResponse:
        """!
        @param uid: uid of the Job to be resumed.
        @return: The Response from the worker client.
        """


class WorkerProxy(IWorkerProxy):
    """
    Implementation of the proxy for the worker client used on the central server.
    """

    @property
    def uid(self) -> str:
        pass

    def dispatch_job(self, job: Job) -> WorkerResponse:
        pass

    def cancel_job(self, uid: str) -> WorkerResponse:
        pass

    def pause_job(self, uid: str) -> WorkerResponse:
        pass

    def resume_job(self, uid: str) -> WorkerResponse:
        pass
