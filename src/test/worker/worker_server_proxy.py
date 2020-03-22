from ja.worker.proxy.proxy import IWorkerServerProxy
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState, WorkMachineResources
from ja.common.job import Job, JobStatus, JobPriority, JobSchedulingConstraints
from ja.common.docker_context import DockerContext, DockerConstraints
from ja.common.message.base import Response
from ja.common.work_machine import ResourceAllocation
from ja.common.proxy.ssh import SSHConfig, ISSHConnection
from typing import Dict
import copy
from unittest import TestCase
from test.abstract import skipIfAbstract


class WorkerServerProxyDummy(IWorkerServerProxy):
    def __init__(self, wmcs: Dict[str, WorkMachine], jobs: Dict[str, Job]):
        self._wmcs: Dict[str, WorkMachine] = copy.deepcopy(wmcs)
        self._jobs: Dict[str, Job] = copy.deepcopy(jobs)

    def register_self(self, uid: str, work_machine_resources: WorkMachineResources) -> Response:
        if uid in self._wmcs:
            return Response("work machine already exist!", False)
        self._wmcs[uid] = WorkMachine(
            uid=uid,
            state=WorkMachineState.ONLINE,
            resources=work_machine_resources
        )
        return Response("work machine added!", True)

    def unregister_self(self, uid: str) -> Response:
        if uid in self._wmcs:
            self._wmcs[uid].state = WorkMachineState.RETIRED
            return Response("work machine unregistred!", True)
        return Response("work machine does not exist!", False)

    def notify_job_finished(self, uid: str) -> Response:
        if uid in self._jobs:
            if self._jobs[uid].status == JobStatus.DONE:
                return Response("job status is already set to DONE!", False)
            else:
                return Response("job finished!", True)
        return Response("job does not exist!", False)

    def notify_job_crashed(self, uid: str) -> Response:
        if uid in self._jobs:
            if self._jobs[uid].status == JobStatus.CRASHED:
                return Response("job status already set to CRASHED!", False)
            else:
                return Response("job finished!", True)
        return Response("job does not exist!", False)

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        pass


class AbstractWorkerServerProxyTest(TestCase):
    def setUp(self) -> None:
        self._job_1 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source="", mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_1.uid = "job-1"
        self._job_1.status = JobStatus.QUEUED
        self._job_1.status = JobStatus.RUNNING
        self._job_2 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source="", mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_2.uid = "job-2"
        self._job_2.status = JobStatus.QUEUED
        self._job_2.status = JobStatus.RUNNING
        self._work_machine_1 = WorkMachine(
            uid="workmachine-1",
            state=WorkMachineState.ONLINE
        )
        self._work_machine_resources = WorkMachineResources(ResourceAllocation(1, 2, 3))
        self._worker_Server_proxy: IWorkerServerProxy = None

    @skipIfAbstract
    def test_register_work_machine(self) -> None:
        response_1 = self._worker_Server_proxy.register_self(self._work_machine_1.uid, self._work_machine_resources)
        self.assertTrue(response_1.is_success)
        response_2 = self._worker_Server_proxy.register_self(self._work_machine_1.uid, self._work_machine_resources)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_unregister_work_machine(self) -> None:
        response_1 = self._worker_Server_proxy.unregister_self(self._work_machine_1.uid)
        self.assertFalse(response_1.is_success)
        response_2 = self._worker_Server_proxy.unregister_self("workmachine-2")
        self.assertTrue(response_2.is_success)

    @skipIfAbstract
    def test_notify_job_finished(self) -> None:
        response_1 = self._worker_Server_proxy.notify_job_finished(self._job_1.uid)
        self.assertTrue(response_1.is_success)
        response_2 = self._worker_Server_proxy.notify_job_finished("bbbbb")
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_notify_job_crashed(self) -> None:
        response_1 = self._worker_Server_proxy.notify_job_crashed(self._job_2.uid)
        self.assertTrue(response_1.is_success)
        response_2 = self._worker_Server_proxy.notify_job_crashed("bbbbb")
        self.assertFalse(response_2.is_success)


class WorkerProxyDummyTest(AbstractWorkerServerProxyTest):
    def setUp(self) -> None:
        super().setUp()
        worker1 = WorkMachine(
            uid="workmachine-2",
            state=WorkMachineState.ONLINE
        )
        wmc = {"workmachine-2": worker1}
        job = {"job-1": self._job_1, "job-2": self._job_2}
        self._worker_Server_proxy = WorkerServerProxyDummy(wmcs=wmc, jobs=job)
