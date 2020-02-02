import ja.server.scheduler.default_policies as dp

from ja.common.job import Job, JobPriority
from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine

from test.abstract import skipIfAbstract
from test.server.scheduler.common import get_job, get_machine
from typing import List, Optional, Tuple
from unittest import TestCase


class DefaultCostFunctionTest(TestCase):
    def setUp(self) -> None:
        self._cost_func = dp.DefaultCostFunction()
        self._low_base = self._cost_func.calculate_cost(get_job(JobPriority.LOW, since=0))
        self._medium_base = self._cost_func.calculate_cost(get_job(JobPriority.MEDIUM, since=0))
        self._high_base = self._cost_func.calculate_cost(get_job(JobPriority.HIGH, since=0))
        self._urgent_base = self._cost_func.calculate_cost(get_job(JobPriority.URGENT, since=0))

    def test_only_urgent_is_preempting(self) -> None:
        self.assertLessEqual(self._urgent_base, self._cost_func.preempting_threshold)
        self.assertLess(self._cost_func.preempting_threshold, self._low_base)
        self.assertLess(self._cost_func.preempting_threshold, self._medium_base)
        self.assertLess(self._cost_func.preempting_threshold, self._high_base)

    def test_priorities_are_ordered(self) -> None:
        self.assertLess(self._urgent_base, self._high_base)
        self.assertLess(self._high_base, self._medium_base)
        self.assertLess(self._medium_base, self._low_base)

    def test_priority_decrease_over_time(self) -> None:
        after_5_mins = self._cost_func.calculate_cost(get_job(JobPriority.MEDIUM, since=5))
        after_15_mins = self._cost_func.calculate_cost(get_job(JobPriority.MEDIUM, since=15))
        self.assertLessEqual(after_15_mins, after_5_mins)
        self.assertLessEqual(after_5_mins, self._medium_base)

    def test_preempt_after_block(self) -> None:
        self.assertLessEqual(self._cost_func.preempting_threshold, self._cost_func.blocking_threshold)


class DummyWorkMachineSelector(dp.DefaultJobDistributionPolicyBase):
    """
    Returns 0 for a predefined work machine, and large costs for the others.
    """
    def __init__(self, chosen: List[WorkMachine], invalid: List[WorkMachine]):
        self._chosen = chosen
        self._invalid = invalid

    def _assign_machine_cost(self,
                             job: Job,
                             machine: WorkMachine,
                             existing_jobs: List[DatabaseJobEntry]) -> Optional[Tuple[float, List[Job]]]:
        if machine in self._chosen:
            return (0.0, [])
        if machine in self._invalid:
            return None

        return (100.0, [])


class DefaultJobDistributionPolicyBaseTest(TestCase):
    def setUp(self) -> None:
        self._machines = [get_machine(10, 10), get_machine(5, 5), get_machine(1, 16)]
        self._job = get_job(JobPriority.MEDIUM).job

    def test_no_suitable_machines(self) -> None:
        selector = DummyWorkMachineSelector([], self._machines)
        self.assertIsNone(selector.assign_machine(job=get_job(JobPriority.MEDIUM, 0).job,
                          distribution=[], available_machines=[]))
        self.assertIsNone(selector.assign_machine(job=get_job(JobPriority.MEDIUM, 0).job,
                          distribution=[], available_machines=self._machines))

    def test_select_only_available(self) -> None:
        selector = DummyWorkMachineSelector(self._machines[-1:], self._machines[:-1])
        self.assertEqual(selector.assign_machine(job=self._job,
                         distribution=[], available_machines=self._machines), (self._machines[-1], []))

    def test_select_best(self) -> None:
        selector = DummyWorkMachineSelector(self._machines[:1], [])
        self.assertEqual(selector.assign_machine(job=self._job,
                         distribution=[], available_machines=self._machines), (self._machines[0], []))

    def test_select_any(self) -> None:
        selector = DummyWorkMachineSelector(self._machines[:1], [])
        self.assertIsNotNone(selector.assign_machine(job=self._job, distribution=[], available_machines=self._machines))


class AbstractDefaultPolicyTest(TestCase):
    @skipIfAbstract
    def setUp(self) -> None:
        self._cpu = 8
        self._ram = 32
        self._job = get_job(JobPriority.MEDIUM, cpu=self._cpu, ram=self._ram).job
        self._policy: dp.DefaultJobDistributionPolicyBase = None

    def test_resources_not_enough(self) -> None:
        machine = get_machine(cpu=self._cpu * 2, ram=self._ram - 1)
        self.assertIsNone(self._policy._assign_machine_cost(self._job, machine, []))
        machine = get_machine(cpu=self._cpu - 1, ram=self._ram * 2)
        self.assertIsNone(self._policy._assign_machine_cost(self._job, machine, []))

    def _get_score(self, machine: WorkMachine, existing_jobs: List[DatabaseJobEntry] = []) -> float:
        result = self._policy._assign_machine_cost(self._job, machine, existing_jobs)
        self.assertIsNotNone(result)
        (cost, preempted) = result
        self.assertListEqual(preempted, [])
        return cost


class DefaultNonPreemptiveDistributionPolicyTest(AbstractDefaultPolicyTest):
    def setUp(self) -> None:
        super().setUp()
        self._policy = dp.DefaultNonPreemptiveDistributionPolicy()

    def test_best_fit(self) -> None:
        machine = get_machine(self._cpu, self._ram)  # perfect fit
        self.assertAlmostEqual(self._get_score(machine), 0.0)

        machine = get_machine(self._cpu + 1, self._ram + 1)  # A little bigger
        almost_fit_score = self._get_score(machine)
        self.assertGreater(almost_fit_score, 0.0)

        machine = get_machine(self._cpu * 5 + 5, self._ram * 5 + 5)  # bad fit
        bad_fit_score = self._get_score(machine)
        self.assertGreater(bad_fit_score, almost_fit_score)


class DefaultBlockingDistributionPolicyTest(AbstractDefaultPolicyTest):
    def setUp(self) -> None:
        super().setUp()
        self._policy = dp.DefaultBlockingDistributionPolicy()
        self._existing = get_job(JobPriority.MEDIUM)

    def test_smallest_number_jobs(self) -> None:
        machine = get_machine(self._cpu, self._ram)  # No Jobs
        self.assertAlmostEqual(self._get_score(machine), 0.0)

        # One Job
        almost_fit_score = self._get_score(machine, existing_jobs=[self._existing])
        self.assertGreater(almost_fit_score, 0.0)

        # Multiple Jobs
        machine = get_machine(self._cpu, self._ram)
        bad_fit_score = self._get_score(machine, existing_jobs=[self._existing] * 5)
        self.assertGreater(bad_fit_score, almost_fit_score)


class DefaultPreemptiveDistributionPolicyTest(AbstractDefaultPolicyTest):
    def setUp(self) -> None:
        super().setUp()
        self._policy = dp.DefaultPreemptiveDistributionPolicy(dp.DefaultCostFunction())
        self._big_high_job = get_job(JobPriority.HIGH, since=10, cpu=self._cpu * 2, ram=self._ram * 2)
        self._high_job = get_job(JobPriority.HIGH, since=10, cpu=self._cpu, ram=self._ram)
        self._medium_job = get_job(JobPriority.MEDIUM, since=5, cpu=self._cpu, ram=self._ram)
        self._low_job = get_job(JobPriority.LOW, since=0, cpu=self._cpu, ram=self._ram)

    def _execute(self, machine: WorkMachine, existing_jobs: List[DatabaseJobEntry]) -> Tuple[float, List[Job]]:
        result = self._policy._assign_machine_cost(self._job, machine, existing_jobs)
        self.assertIsNotNone(result)
        return result

    def test_free_machine(self) -> None:
        machine = get_machine(self._cpu, self._ram)  # No Jobs
        self.assertAlmostEqual(self._get_score(machine), 0.0)

    def test_preempt_all_jobs(self) -> None:
        machine = get_machine(self._cpu, self._ram)
        machine.resources.allocate(ResourceAllocation(self._cpu, self._ram, 0))

        (almost_fit_score, preempt) = self._execute(machine, existing_jobs=[self._medium_job])
        self.assertGreater(almost_fit_score, 0.0)
        self.assertListEqual(preempt, [self._medium_job.job])

    def test_preempt_some_jobs(self) -> None:
        # 3 Jobs, preempt only 2
        machine = get_machine(self._cpu * 4, self._ram * 4)
        # Needs to suspend other jobs
        self._job = get_job(JobPriority.URGENT, cpu=self._cpu * 2, ram=self._ram * 2).job

        machine.resources.allocate(ResourceAllocation(self._cpu * 4, self._cpu * 4, 0))  # 4xhigh job
        (bad_fit, bad_preempt) = \
            self._execute(machine, existing_jobs=[self._high_job] * 4)
        (med_fit, med_preempt) = \
            self._execute(machine, existing_jobs=[self._big_high_job, self._medium_job, self._medium_job])
        (good_fit, good_preempt) = \
            self._execute(machine, existing_jobs=[self._high_job, self._medium_job, self._medium_job, self._low_job])

        self.assertGreater(bad_fit, med_fit)
        self.assertGreater(med_fit, good_fit)

        self.assertCountEqual(bad_preempt, [self._high_job.job, self._high_job.job])
        self.assertCountEqual(med_preempt, [self._medium_job.job, self._medium_job.job])
        self.assertCountEqual(good_preempt, [self._low_job.job, self._medium_job.job])
