import ja.server.scheduler.default_policies as dp

from ja.common.job import JobPriority, JobStatus
from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.scheduler.algorithm import CostFunction, get_allocation_for_job
from ja.server.scheduler.default_algorithm import DefaultSchedulingAlgorithm
from test.server.scheduler.common import get_job, get_scheduled_job, get_machine, assert_distributions_equal
from typing import Tuple
from unittest import TestCase


class SimpleCostFunction(CostFunction):
    _fixed_cost = {
        JobPriority.URGENT: 0,
        JobPriority.HIGH: 1,
        JobPriority.MEDIUM: 2,
        JobPriority.LOW: 3,
    }

    def calculate_cost(self, job: DatabaseJobEntry) -> float:
        return self._fixed_cost[job.job.scheduling_constraints.priority]

    @property
    def blocking_threshold(self) -> float:
        return self._fixed_cost[JobPriority.HIGH]

    @property
    def preempting_threshold(self) -> float:
        return self._fixed_cost[JobPriority.URGENT]


class AllocationForJobTest(TestCase):
    def test_running_job(self) -> None:
        job = get_job(JobPriority.MEDIUM, cpu=8, ram=16).job
        job.status = JobStatus.RUNNING
        allocation = get_allocation_for_job(job)
        self.assertEqual(allocation, ResourceAllocation(8, 16, 0))

    def test_paused_job(self) -> None:
        job = get_job(JobPriority.MEDIUM, cpu=8, ram=16).job
        job.status = JobStatus.RUNNING
        job.status = JobStatus.PAUSED
        allocation = get_allocation_for_job(job)
        self.assertEqual(allocation, ResourceAllocation(0, 0, 16))


class DefaultSchedulingAlgorithmTest(TestCase):
    def setUp(self) -> None:
        cost_func = SimpleCostFunction()
        self._algo = DefaultSchedulingAlgorithm(cost_func, dp.DefaultNonPreemptiveDistributionPolicy(cost_func),
                                                dp.DefaultBlockingDistributionPolicy(),
                                                dp.DefaultPreemptiveDistributionPolicy(cost_func))
        self._cpu = 8
        self._ram = 8
        self._machine = get_machine(cpu=self._cpu * 2, ram=self._ram * 2, swap=self._ram * 3)
        self._filler: DatabaseJobEntry = \
            get_job(JobPriority.MEDIUM, cpu=self._cpu, ram=self._ram, machine=self._machine)
        self._filler.job.status = JobStatus.RUNNING
        self._machine.resources.allocate(get_allocation_for_job(self._filler.job))

    def test_no_runnable_jobs(self) -> None:
        old_schedule = [self._filler]
        new_schedule = self._algo.reschedule_jobs(old_schedule, [self._machine], {})
        assert_distributions_equal(self, new_schedule, old_schedule)

    def test_pick_higher_priority_job(self) -> None:
        high_job = get_job(JobPriority.MEDIUM, since=100, cpu=self._cpu, ram=self._ram)
        low_job = get_job(JobPriority.LOW, since=0, cpu=self._cpu, ram=self._ram)

        old_schedule = [self._filler, high_job, low_job]
        new_schedule = self._algo.reschedule_jobs(old_schedule, [self._machine], {})

        self._machine.resources.allocate(get_allocation_for_job(high_job.job))
        expected_schedule = [
            self._filler,
            get_scheduled_job(high_job, self._machine, JobStatus.RUNNING),
            low_job,
        ]
        assert_distributions_equal(self, new_schedule, expected_schedule)

    def _blocking_test_intro(self) -> Tuple[DatabaseJobEntry, DatabaseJobEntry]:
        # SimpleCostFunction guarantees HIGH priority jobs are blocking
        big_job = get_job(JobPriority.HIGH, cpu=self._cpu * 2, ram=self._ram * 2)
        low_job = get_job(JobPriority.LOW, since=0, cpu=self._cpu, ram=self._ram)

        # Blocking job comes, work machine is reserved for it
        first_schedule = [self._filler, big_job]
        new_schedule = self._algo.reschedule_jobs(first_schedule, [self._machine], {})
        assert_distributions_equal(self, new_schedule, first_schedule)

        # A low priority job comes. It is not scheduled on a blocked machine
        second_schedule = [self._filler, big_job, low_job]
        new_schedule = self._algo.reschedule_jobs(second_schedule, [self._machine], {})
        assert_distributions_equal(self, new_schedule, second_schedule)
        return (big_job, low_job)

    def test_use_blocked_machine(self) -> None:
        (big_job, low_job) = self._blocking_test_intro()

        # Old filler job is completed. Blocking job goes to reserved machine, low priority job needs to wait
        third_schedule = [big_job, low_job]
        self._machine.resources.deallocate(get_allocation_for_job(self._filler.job))

        new_schedule = self._algo.reschedule_jobs(third_schedule, [self._machine], {})
        expected_schedule = [
            get_scheduled_job(big_job, self._machine, JobStatus.RUNNING),
            low_job
        ]
        assert_distributions_equal(self, new_schedule, expected_schedule)

    def test_not_use_blocked_machine(self) -> None:
        (big_job, low_job) = self._blocking_test_intro()

        # Filler job is still running, but we get a new machine where we can schedule the blocking job directly.
        # This unblocks the blocked machine for the low job machine.
        third_schedule = [big_job, low_job, self._filler]
        new_machine = get_machine(cpu=self._cpu * 2, ram=self._ram * 2)
        new_schedule = self._algo.reschedule_jobs(third_schedule, [self._machine, new_machine], {})
        expected_schedule = [
            self._filler,
            get_scheduled_job(big_job, new_machine, JobStatus.RUNNING),
            get_scheduled_job(low_job, self._machine, JobStatus.RUNNING)
        ]
        assert_distributions_equal(self, new_schedule, expected_schedule)

    def test_urgent_overrides_block(self) -> None:
        (big_job, low_job) = self._blocking_test_intro()
        # Urgent jobs should not be affected by reserved/blocked machines.
        urgent_job = get_job(JobPriority.URGENT, cpu=self._cpu * 2, ram=self._ram * 2)
        new_schedule = self._algo.reschedule_jobs([self._filler, big_job, low_job, urgent_job], [self._machine], {})
        expected_schedule = [
            get_scheduled_job(self._filler, self._machine, JobStatus.PAUSED),
            big_job,
            low_job,
            get_scheduled_job(urgent_job, self._machine, JobStatus.RUNNING)
        ]
        assert_distributions_equal(self, expected_schedule, new_schedule)

        # However, after the urgent job is done, the block still remains
        new_schedule = self._algo.reschedule_jobs([self._filler, big_job, low_job], [self._machine], {})
        assert_distributions_equal(self, new_schedule, [self._filler, big_job, low_job])

    def test_preemption(self) -> None:
        # Two machines, one has 1 job, other has 2 jobs
        # We want to preempt the job on the machine which has only 1 job.
        urgent_job = get_job(JobPriority.URGENT, cpu=self._cpu * 2, ram=self._ram * 2)

        # Other machine
        other_machine = get_machine(cpu=self._cpu * 3, ram=self._ram * 3)
        existing_low_job1 = get_job(JobPriority.MEDIUM, cpu=self._cpu, ram=int(self._ram * 1.5), machine=other_machine)
        existing_low_job2 = get_job(JobPriority.MEDIUM, cpu=self._cpu, ram=int(self._ram * 1.5), machine=other_machine)
        other_machine.resources.allocate(get_allocation_for_job(existing_low_job1.job))
        other_machine.resources.allocate(get_allocation_for_job(existing_low_job2.job))
        existing_low_job1.job.status = JobStatus.RUNNING
        existing_low_job2.job.status = JobStatus.RUNNING

        old_schedule = [existing_low_job1, existing_low_job2, self._filler, urgent_job]
        new_schedule = self._algo.reschedule_jobs(old_schedule, [self._machine, other_machine], {})
        expected_schedule = [
            existing_low_job1,
            existing_low_job2,
            get_scheduled_job(urgent_job, self._machine, JobStatus.RUNNING),
            get_scheduled_job(self._filler, self._machine, JobStatus.PAUSED)
        ]
        self._machine.resources.deallocate(get_allocation_for_job(self._filler.job))
        self._machine.resources.allocate(ResourceAllocation(0, 0, self._filler.job.docker_constraints.memory))
        self._machine.resources.allocate(get_allocation_for_job(urgent_job.job))
        assert_distributions_equal(self, new_schedule, expected_schedule)

        # Urgent job is done, restore filler job
        self._machine.resources.deallocate(get_allocation_for_job(urgent_job.job))
        old_schedule = [
            existing_low_job1,
            existing_low_job2,
            get_scheduled_job(self._filler, self._machine, JobStatus.PAUSED)
        ]
        new_schedule = self._algo.reschedule_jobs(old_schedule, [self._machine, other_machine], {})
        assert_distributions_equal(self, new_schedule, [existing_low_job1, existing_low_job2, self._filler])

    def test_restore_paused_first(self) -> None:
        # Preempt filler job
        self._machine.resources.deallocate(get_allocation_for_job(self._filler.job))
        self._filler.job.status = JobStatus.PAUSED
        self._machine.resources.allocate(get_allocation_for_job(self._filler.job))

        # A new big job, which cannot run concurrently with filler
        large_job = get_job(JobPriority.HIGH, cpu=self._cpu * 2, ram=self._ram * 2)
        new_schedule = self._algo.reschedule_jobs([large_job, self._filler], [self._machine], {})
        expected_schedule = [
            get_scheduled_job(self._filler, self._machine, JobStatus.RUNNING),
            large_job
        ]
        assert_distributions_equal(self, new_schedule, expected_schedule)

    def test_special_resources(self) -> None:
        high_job = get_job(JobPriority.MEDIUM, cpu=self._cpu + 1, ram=self._ram, special_resources=["A"])
        medium_job = get_job(JobPriority.MEDIUM, cpu=self._cpu, ram=self._ram, special_resources=["A", "B", "B"])
        low_job = get_job(JobPriority.LOW, cpu=self._cpu, ram=self._ram, special_resources=["A", "A"])

        current_schedule = [high_job, medium_job, low_job, self._filler]
        new_schedule = self._algo.reschedule_jobs(current_schedule, [self._machine], {"A": 2, "B": 1})
        expected_schedule = [
            high_job,
            medium_job,
            get_scheduled_job(low_job, self._machine, JobStatus.RUNNING),
            self._filler
        ]
        assert_distributions_equal(self, new_schedule, expected_schedule)
