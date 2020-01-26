from typing import List
from unittest import TestCase

from ja.common.job import Job, JobStatus, JobPriority, JobSchedulingConstraints
from ja.common.docker_context import DockerContext, DockerConstraints
from ja.common.message.worker import WorkerResponse
from ja.server.proxy.proxy import IWorkerProxy
from test.abstract import skipIfAbstract


class WorkerProxyDummy(IWorkerProxy):
    def __init__(self, uid: str, jobs: List[Job]):
        self._uid = uid
        self._jobs: List[Job] = []
        for job in jobs:
            job_copy = Job.from_dict(job.to_dict())
            job_copy.status = JobStatus.RUNNING
            self._jobs.append(job_copy)

    def _find_job(self, uid: str) -> Job:
        for job in self._jobs:
            if job.uid == uid:
                return job
        return None

    @property
    def uid(self) -> str:
        return self._uid

    def dispatch_job(self, job: Job) -> WorkerResponse:
        for existing_job in self._jobs:
            if job.uid == existing_job.uid:
                return WorkerResponse.from_dict(WorkerResponse(
                    result_string=IWorkerProxy.DISPATCH_JOB_DUPLICATE % (job.uid, self.uid), is_success=False
                ).to_dict())
        job_copy = Job.from_dict(job.to_dict())
        job_copy._status = JobStatus.RUNNING
        self._jobs.append(job_copy)
        return WorkerResponse.from_dict(WorkerResponse(
            result_string=IWorkerProxy.DISPATCH_JOB_SUCCESS % (job.uid, self.uid), is_success=True).to_dict())

    def cancel_job(self, uid: str) -> WorkerResponse:
        for job in self._jobs:
            if uid == job.uid:
                job.status = JobStatus.CANCELLED
                self._jobs.remove(job)
                return WorkerResponse.from_dict(WorkerResponse(
                    result_string=IWorkerProxy.CANCEL_JOB_SUCCESS % (uid, self.uid), is_success=True).to_dict())
        return WorkerResponse.from_dict(WorkerResponse(
            result_string=IWorkerProxy.CANCEL_JOB_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())

    def pause_job(self, uid: str) -> WorkerResponse:
        for job in self._jobs:
            if uid == job.uid:
                try:
                    job.status = JobStatus.PAUSED
                    return WorkerResponse.from_dict(WorkerResponse(
                        result_string=IWorkerProxy.PAUSE_JOB_SUCCESS % (uid, self.uid), is_success=True).to_dict())
                except ValueError:
                    return WorkerResponse.from_dict(WorkerResponse(
                        result_string=IWorkerProxy.PAUSE_JOB_NOT_RUNNING % (uid, self.uid), is_success=False
                    ).to_dict())
        return WorkerResponse.from_dict(WorkerResponse(
            result_string=IWorkerProxy.PAUSE_JOB_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())

    def resume_job(self, uid: str) -> WorkerResponse:
        for job in self._jobs:
            if uid == job.uid:
                try:
                    job.status = JobStatus.RUNNING
                    return WorkerResponse.from_dict(WorkerResponse(
                        result_string=IWorkerProxy.RESUME_JOB_SUCCESS % (uid, self.uid), is_success=True).to_dict())
                except ValueError:
                    return WorkerResponse.from_dict(WorkerResponse(
                        result_string=IWorkerProxy.RESUME_JOB_NOT_PAUSED % (uid, self.uid), is_success=False
                    ).to_dict())
        return WorkerResponse.from_dict(WorkerResponse(
            result_string=IWorkerProxy.RESUME_JOB_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())


class AbstractWorkerProxyTest(TestCase):
    def setUp(self) -> None:
        self._uid_1 = "job-1"
        self._job_1 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source="", mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_1.uid = self._uid_1
        self._job_1.status = JobStatus.QUEUED
        self._uid_2 = "job-2"
        self._job_2 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source="", mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_2.uid = self._uid_2
        self._job_2.status = JobStatus.QUEUED
        self._uid_unknown = "DEADBEEF"
        self._empty_worker: IWorkerProxy = None
        self._busy_worker: IWorkerProxy = None

    @skipIfAbstract
    def test_dispatch_to_empty_worker(self) -> None:
        response_1 = self._empty_worker.dispatch_job(self._job_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._empty_worker.dispatch_job(self._job_2)
        self.assertTrue(response_2.is_success)

    @skipIfAbstract
    def dispatch_to_busy_worker(self) -> None:
        response_1 = self._busy_worker.dispatch_job(self._job_1)
        self.assertFalse(response_1.is_success)
        response_2 = self._busy_worker.dispatch_job(self._job_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_dispatch_same_job_twice_1(self) -> None:
        response_1 = self._empty_worker.dispatch_job(self._job_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._empty_worker.dispatch_job(self._job_1)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_dispatch_same_job_twice_2(self) -> None:
        response_1 = self._empty_worker.dispatch_job(self._job_2)
        self.assertTrue(response_1.is_success)
        response_2 = self._empty_worker.dispatch_job(self._job_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_cancel_empty_worker(self) -> None:
        response_1 = self._empty_worker.cancel_job(self._uid_1)
        self.assertFalse(response_1.is_success)
        response_2 = self._empty_worker.cancel_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_cancel_busy_worker(self) -> None:
        response_1 = self._busy_worker.cancel_job(self._uid_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.cancel_job(self._uid_2)
        self.assertTrue(response_2.is_success)

    @skipIfAbstract
    def test_cancel_same_job_twice_1(self) -> None:
        response_1 = self._busy_worker.cancel_job(self._uid_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.cancel_job(self._uid_1)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_cancel_same_job_twice_2(self) -> None:
        response_1 = self._busy_worker.cancel_job(self._uid_2)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.cancel_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_cancel_unknown(self) -> None:
        response_empty = self._empty_worker.cancel_job(self._uid_unknown)
        self.assertFalse(response_empty.is_success)
        response_busy = self._empty_worker.cancel_job(self._uid_unknown)
        self.assertFalse(response_busy.is_success)

    @skipIfAbstract
    def test_pause_empty_worker(self) -> None:
        response_1 = self._empty_worker.pause_job(self._uid_1)
        self.assertFalse(response_1.is_success)
        response_2 = self._empty_worker.pause_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_pause_busy_worker(self) -> None:
        response_1 = self._busy_worker.pause_job(self._uid_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.pause_job(self._uid_2)
        self.assertTrue(response_2.is_success)

    @skipIfAbstract
    def test_pause_same_job_twice_1(self) -> None:
        response_1 = self._busy_worker.pause_job(self._uid_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.pause_job(self._uid_1)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_pause_same_job_twice_2(self) -> None:
        response_1 = self._busy_worker.pause_job(self._uid_2)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.pause_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_pause_unknown(self) -> None:
        response_empty = self._empty_worker.pause_job(self._uid_unknown)
        self.assertFalse(response_empty.is_success)
        response_busy = self._empty_worker.pause_job(self._uid_unknown)
        self.assertFalse(response_busy.is_success)

    @skipIfAbstract
    def test_resume_empty_worker(self) -> None:
        response_1 = self._empty_worker.resume_job(self._uid_1)
        self.assertFalse(response_1.is_success)
        response_2 = self._empty_worker.resume_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_resume_busy_worker(self) -> None:
        response_1 = self._busy_worker.resume_job(self._uid_1)
        self.assertFalse(response_1.is_success)
        response_2 = self._busy_worker.resume_job(self._uid_2)
        self.assertFalse(response_2.is_success)

    @skipIfAbstract
    def test_pause_resume_1(self) -> None:
        response_1 = self._busy_worker.pause_job(self._uid_1)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.resume_job(self._uid_2)
        self.assertFalse(response_2.is_success)
        response_3 = self._busy_worker.resume_job(self._uid_1)
        self.assertTrue(response_3.is_success)

    @skipIfAbstract
    def test_pause_resume_2(self) -> None:
        response_1 = self._busy_worker.pause_job(self._uid_2)
        self.assertTrue(response_1.is_success)
        response_2 = self._busy_worker.resume_job(self._uid_1)
        self.assertFalse(response_2.is_success)
        response_3 = self._busy_worker.resume_job(self._uid_2)
        self.assertTrue(response_3.is_success)

    @skipIfAbstract
    def test_resume_unknown(self) -> None:
        response_empty = self._empty_worker.resume_job(self._uid_unknown)
        self.assertFalse(response_empty.is_success)
        response_busy = self._empty_worker.resume_job(self._uid_unknown)
        self.assertFalse(response_busy.is_success)


class WorkerProxyDummyTest(AbstractWorkerProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self._empty_worker = WorkerProxyDummy(uid="empty-worker", jobs=[])
        self._busy_worker = WorkerProxyDummy(uid="busy-worker", jobs=[self._job_1, self._job_2])
