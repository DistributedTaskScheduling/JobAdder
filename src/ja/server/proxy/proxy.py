from abc import ABC, abstractmethod

from ja.common.proxy.proxy import ContinuousProxy
from ja.common.proxy.ssh import SSHConfig
from ja.common.message.worker import WorkerResponse
from ja.common.job import Job


class IWorkerProxy(ContinuousProxy, ABC):
    """
    Interface for the proxy for the worker client used on the central server.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko.
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

    def dispatch_job(self, job: Job) -> WorkerResponse:
        pass

    def cancel_job(self, uid: str) -> WorkerResponse:
        pass

    def pause_job(self, uid: str) -> WorkerResponse:
        pass

    def resume_job(self, uid: str) -> WorkerResponse:
        pass
