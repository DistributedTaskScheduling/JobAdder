from ja.common.job import JobStatus, Job
from ja.server.scheduler.default_policies import DefaultCostFunction
from test.integration.base import IntegrationTest
from time import sleep
from typing import Any, List, Tuple


class TestScheduler(IntegrationTest):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.list_updates: List[Tuple[str, JobStatus]] = []

    def _status_updated(self, job: Job) -> None:
        self.list_updates.append((job.label, job.status))

    def test_three_jobs(self) -> None:
        """
        A test where 3 jobs with different priorities are scheduled, and then a worker is added.
        """
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=1, label="lo", priority="0", threads=4, memory=16 * 1024))
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=1, label="me", priority="1", threads=4, memory=16 * 1024))
        self._clients[2].run(
            self.get_arg_list_add(num_seconds=1, label="hi", priority="3", threads=4, memory=16 * 1024))
        self._server._database.set_job_status_callback(self._status_updated)
        self._add_worker(0)
        sleep(25)
        expect: List[Tuple[str, JobStatus]] = [
            ("hi", JobStatus.RUNNING),
            ("hi", JobStatus.DONE),
            ("me", JobStatus.RUNNING),
            ("me", JobStatus.DONE),
            ("lo", JobStatus.RUNNING),
            ("lo", JobStatus.DONE),
        ]
        self.assertListEqual(self.list_updates, expect)

    def test_parallel_jobs(self) -> None:
        """
        A test where 3 jobs are scheduled on 2 workers
        """
        self._add_worker(0)
        self._add_worker(1)
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=60, label="lo", priority="0", threads=4, memory=16 * 1024))
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=60, label="me", priority="1", threads=2, memory=8 * 1024))
        self._clients[2].run(
            self.get_arg_list_add(num_seconds=60, label="hi", priority="3", threads=2, memory=8 * 1024))
        sleep(1)
        # Jobs can't have finished so they are all in the schedule
        distribution = self._server._database.get_current_schedule()
        workers = sorted([job.assigned_machine.uid for job in distribution])

        v1 = ["worker_0", "worker_0", "worker_1"]
        v2 = ["worker_0", "worker_1", "worker_1"]
        if workers != v1 and workers != v2:
            self.assertTrue(False, "Distribution %s does not match any of the expected values!" % str(workers))

    def test_preemption(self) -> None:
        """
        A test where a low-prio job is preempted because of an urgent job.
        """
        self._add_worker(0)
        self._server._database.set_job_status_callback(self._status_updated)
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=5, label="lo", priority="0", threads=4, memory=16 * 1024))
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=1, label="ur", priority="3", threads=4, memory=16 * 1024))
        sleep(8)
        expect: List[Tuple[str, JobStatus]] = [
            ("lo", JobStatus.RUNNING),
            ("lo", JobStatus.PAUSED),
            ("ur", JobStatus.RUNNING),
            ("ur", JobStatus.DONE),
            ("lo", JobStatus.RUNNING),
            ("lo", JobStatus.DONE),
        ]
        self.assertListEqual(expect, self.list_updates)

    def test_blocking(self) -> None:
        """
        A complicated test involving blocking and preemption.
        """
        self._add_worker(0)
        DefaultCostFunction._multiplier = 0
        self._server._database.set_job_status_callback(self._status_updated)
        # Occupy half the machine
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=12, label="lo", priority="0", threads=2, memory=8 * 1024))
        # This one should reserve the machine since it is blocking
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=2, label="hi", priority="2", threads=4, memory=16 * 1024))
        # Won't run anytime soon since machine is reserved
        self._clients[2].run(
            self.get_arg_list_add(num_seconds=2, label="me", priority="1", threads=2, memory=8 * 1024))
        # Urgent jobs however should override blocking
        self._clients[3].run(
            self.get_arg_list_add(num_seconds=2, label="ur", priority="3", threads=3, memory=8 * 1024))
        sleep(20)
        expect: List[Tuple[str, JobStatus]] = [
            ("lo", JobStatus.RUNNING),
            ("lo", JobStatus.PAUSED),
            ("ur", JobStatus.RUNNING),
            ("ur", JobStatus.DONE),
            ("lo", JobStatus.RUNNING),
            ("lo", JobStatus.DONE),
            ("hi", JobStatus.RUNNING),
            ("hi", JobStatus.DONE),
            ("me", JobStatus.RUNNING),
            ("me", JobStatus.DONE),
        ]
        self.assertListEqual(expect, self.list_updates)

    @property
    def num_workers(self) -> int:
        return 0

    @property
    def num_clients(self) -> int:
        return 4
