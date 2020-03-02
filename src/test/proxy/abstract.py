from unittest import TestCase

from ja.common.job import Job, JobStatus, JobPriority, JobSchedulingConstraints
from ja.common.docker_context import DockerContext, DockerConstraints
from ja.server.proxy.proxy import IWorkerProxy
from test.abstract import skipIfAbstract


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
