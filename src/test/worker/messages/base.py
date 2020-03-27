from ja.common.job import JobStatus
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.scheduler.algorithm import get_allocation_for_job
from ja.worker.message.base import WorkerServerCommand
from test.server.scheduler.common import get_machine, get_job
from unittest import TestCase


class WorkerMessageBaseTest(TestCase):
    def setUp(self) -> None:
        self._db = MockDatabase()
        self._job = get_job(status=JobStatus.QUEUED).job
        self._db.update_job(self._job)
        self._job.status = JobStatus.RUNNING
        self._db.update_job(self._job)

    def test_free_resources_for_running(self) -> None:
        machine = get_machine(8, 8, 8)
        machine.resources.allocate(get_allocation_for_job(self._job))
        machine.state = WorkMachineState.RETIRED
        self._db.update_work_machine(machine)
        self._db.assign_job_machine(self._job, machine)

        WorkerServerCommand._free_resources_for_job(self._db, self._db.find_job_by_id(self._job.uid), JobStatus.DONE)

        updated = self._db.find_job_by_id(self._job.uid)
        self.assertEqual(updated.job.status, JobStatus.DONE)
        self.assertEqual(updated.assigned_machine, None)

        machine = [m for m in self._db.get_all_work_machines() if m.uid == machine.uid][0]
        self.assertEqual(machine.state, WorkMachineState.OFFLINE)
        self.assertEqual(machine.resources.free_resources, machine.resources.total_resources)

    def test_free_resources_for_queued(self) -> None:
        WorkerServerCommand._free_resources_for_job(self._db,
                                                    self._db.find_job_by_id(self._job.uid),
                                                    JobStatus.CRASHED)

        updated = self._db.find_job_by_id(self._job.uid)
        self.assertEqual(updated.job.status, JobStatus.CRASHED)
        self.assertEqual(updated.assigned_machine, None)
