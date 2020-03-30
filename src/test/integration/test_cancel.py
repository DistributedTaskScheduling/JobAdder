from ja.common.job import JobStatus
from ja.common.work_machine import ResourceAllocation
from test.integration.base import IntegrationTest
from time import sleep
from typing import Any, List, Tuple


class TestJobCancel(IntegrationTest):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.list_updates: List[Tuple[str, JobStatus]] = []

    def test_cancel(self) -> None:
        """
        Run one job, queue another and cancel both.
        """
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=5, label="lo", priority="0", threads=4, memory=16 * 1024))
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=1, label="me", priority="1", threads=4, memory=16 * 1024))
        sleep(1)  # Wait for first job to get scheduled
        self._clients[2].run(["cancel", "-l", "me"])
        jobs = self._server._database.query_jobs(None, -1, None)
        db_lo = [job for job in jobs if job.job.label == "lo"][0]
        db_me = [job for job in jobs if job.job.label == "me"][0]
        db_wm = self._server._database.get_all_work_machines()[0]
        self.assertEqual(db_lo.job.status, JobStatus.RUNNING)
        self.assertEqual(db_me.job.status, JobStatus.CANCELLED)
        self.assertEqual(db_wm.resources.free_resources, ResourceAllocation(0, 0, 16 * 1024))
        self.assertEqual(len(self._workers[0]._docker_interface._jobs_by_container_id), 1)
        self._clients[3].run(["cancel", "-l", "lo"])

        jobs = self._server._database.query_jobs(None, -1, None)
        db_lo = [job for job in jobs if job.job.label == "lo"][0]
        db_me = [job for job in jobs if job.job.label == "me"][0]
        db_wm = self._server._database.get_all_work_machines()[0]
        self.assertEqual(db_lo.job.status, JobStatus.CANCELLED)
        self.assertEqual(db_me.job.status, JobStatus.CANCELLED)
        self.assertEqual(db_wm.resources.free_resources, ResourceAllocation(4, 16 * 1024, 16 * 1024))
        self.assertEqual(len(self._workers[0]._docker_interface._jobs_by_container_id), 0)

    @property
    def num_workers(self) -> int:
        return 1

    @property
    def num_clients(self) -> int:
        return 4
