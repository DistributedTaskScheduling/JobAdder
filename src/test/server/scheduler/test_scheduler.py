from ja.common.job import JobStatus
from ja.common.work_machine import ResourceAllocation
from ja.server.database.database import ServerDatabase
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState
from ja.server.dispatcher.dispatcher import Dispatcher
from ja.server.scheduler.algorithm import SchedulingAlgorithm
from ja.server.scheduler.scheduler import Scheduler

from test.server.scheduler.common import get_job, get_machine, get_scheduled_job
from test.server.scheduler.common import assert_distributions_equal, assert_items_equal

from typing import List, Dict
from unittest import TestCase


class MockAlgorithm(SchedulingAlgorithm):
    def __init__(self,
                 test_case: TestCase,
                 expect_schedule: ServerDatabase.JobDistribution,
                 expect_machines: List[WorkMachine],
                 expect_resources: Dict[str, int],
                 return_schedule: ServerDatabase.JobDistribution):
        self._test_case: TestCase = test_case
        self._expect_schedule = expect_schedule
        self._expect_machines = expect_machines
        self._expect_resources = expect_resources
        self._return = return_schedule

    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine],
                        available_special_resources: Dict[str, int]) -> ServerDatabase.JobDistribution:
        assert_distributions_equal(self._test_case, self._expect_schedule, current_schedule)
        machine_list = [(m.uid, m.resources) for m in available_machines]
        expect_list = [(m.uid, m.resources) for m in self._expect_machines]
        assert_items_equal(self._test_case, machine_list, expect_list)
        self._test_case.assertDictEqual(self._expect_resources, available_special_resources)

        return self._return


class MockDispatcher(Dispatcher):
    def __init__(self, test_case: TestCase, expect_schedule: ServerDatabase.JobDistribution):
        self._test_case = test_case
        self._expect = expect_schedule
        self.count_called = 0

    def set_distribution(self, job_distribution: ServerDatabase.JobDistribution) -> None:
        self.count_called += 1
        assert_distributions_equal(self._test_case, job_distribution, self._expect)


class SchedulerTest(TestCase):
    def test_scheduler_updates(self) -> None:
        db = MockDatabase()

        machine1 = get_machine(8, 8, 8)
        machine1.resources.allocate(ResourceAllocation(0, 0, 4))
        machine2 = get_machine(4, 16, 7)
        machine2.resources.allocate(ResourceAllocation(3, 2, 0))
        machine3 = get_machine(1, 1)
        machine3.state = WorkMachineState.RETIRED
        machine4 = get_machine(1, 1)
        machine4.state = WorkMachineState.OFFLINE
        for machine in [machine1, machine2, machine3, machine4]:
            db.update_work_machine(machine)

        job1 = get_job(status=JobStatus.QUEUED, cpu=1, ram=4, machine=machine1)
        job2 = get_job(status=JobStatus.QUEUED, cpu=3, ram=2, machine=machine2)
        job3 = get_job(status=JobStatus.QUEUED, cpu=2, ram=15, special_resources=['A', 'B'])
        job4 = get_job(status=JobStatus.QUEUED, cpu=128, ram=128)
        current_schedule = [job1, job2, job3, job4]
        for job in current_schedule:
            db.update_job(job.job)
            db.assign_job_machine(job.job, job.assigned_machine)
        # Change status of job1 and job2
        job1.job.status = job2.job.status = JobStatus.RUNNING
        db.update_job(job1.job)
        db.update_job(job2.job)
        job1.job.status = JobStatus.PAUSED
        db.update_job(job1.job)

        special_resources = {'A': 2, 'B': 1}
        result_schedule = [
            get_scheduled_job(job1, machine=machine1, next_status=JobStatus.RUNNING),
            get_scheduled_job(job2, machine=machine2, next_status=JobStatus.PAUSED),
            get_scheduled_job(job3, machine=machine2, next_status=JobStatus.RUNNING),
            job4
        ]

        algo = MockAlgorithm(self, current_schedule, [machine1, machine2], special_resources, result_schedule)
        dispatcher = MockDispatcher(self, result_schedule)
        scheduler = Scheduler(algo, dispatcher, special_resources)
        self.assertDictEqual(scheduler.total_special_resources, special_resources)
        scheduler.reschedule(db)

        # Verify output
        assert_distributions_equal(self, db.get_current_schedule(), result_schedule)
        self.assertDictEqual(scheduler.special_resources, {'A': 1, 'B': 0})
        self.assertDictEqual(scheduler.total_special_resources, special_resources)

        db_machines = db.get_work_machines()
        db_machine1 = [m for m in db_machines if m.uid == machine1.uid][0]
        db_machine2 = [m for m in db_machines if m.uid == machine2.uid][0]
        self.assertEqual(db_machine1.resources.free_resources, ResourceAllocation(7, 4, 8))
        self.assertEqual(db_machine2.resources.free_resources, ResourceAllocation(2, 1, 5))
        self.assertEqual(dispatcher.count_called, 1)
