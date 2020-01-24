import datetime as dt
import ja.common.job as jb
import ja.common.work_machine as cwm
import ja.server.database.types.job_entry as je
import ja.server.database.types.work_machine as wm
import ja.server.scheduler.default_policies as dp

from unittest import TestCase
from typing import List, Optional, Tuple


def _datetime_before(since: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=since)


def _get_job(prio: jb.JobPriority, since: int) -> je.DatabaseJobEntry:
    job = jb.Job(owner_id=0, email="hey@you", scheduling_constraints=jb.JobSchedulingConstraints(prio, False, []),
                 docker_context=None, docker_constraints=None)
    stats = je.JobRuntimeStatistics(_datetime_before(since), dt.datetime.now(), 0)
    return je.DatabaseJobEntry(job, stats, None)


class DefaultCostFunctionTest(TestCase):
    def setUp(self) -> None:
        self.cost_func = dp.DefaultCostFunction()
        self.low_base = self.cost_func.calculate_cost(_get_job(jb.JobPriority.LOW, 0))
        self.medium_base = self.cost_func.calculate_cost(_get_job(jb.JobPriority.MEDIUM, 0))
        self.high_base = self.cost_func.calculate_cost(_get_job(jb.JobPriority.HIGH, 0))
        self.urgent_base = self.cost_func.calculate_cost(_get_job(jb.JobPriority.URGENT, 0))

    def test_only_urgent_is_preempting(self) -> None:
        self.assertLessEqual(self.urgent_base, self.cost_func.preempting_threshold)
        self.assertLess(self.cost_func.preempting_threshold, self.low_base)
        self.assertLess(self.cost_func.preempting_threshold, self.medium_base)
        self.assertLess(self.cost_func.preempting_threshold, self.high_base)

    def test_priorities_are_ordered(self) -> None:
        self.assertLess(self.urgent_base, self.high_base)
        self.assertLess(self.high_base, self.medium_base)
        self.assertLess(self.medium_base, self.low_base)

    def test_priority_decrease_over_time(self) -> None:
        after_5_mins = self.cost_func.calculate_cost(_get_job(jb.JobPriority.MEDIUM, 5))
        after_15_mins = self.cost_func.calculate_cost(_get_job(jb.JobPriority.MEDIUM, 15))
        self.assertLessEqual(after_15_mins, after_5_mins)
        self.assertLessEqual(after_5_mins, self.medium_base)

    def test_preempt_after_block(self) -> None:
        self.assertLessEqual(self.cost_func.preempting_threshold, self.cost_func.blocking_threshold)


class DummyWorkMachineSelector(dp.DefaultJobDistributionPolicyBase):
    """
    Returns 0 for a predefined work machine, and large costs for the others.
    """
    def __init__(self, chosen: List[wm.WorkMachine], invalid: List[wm.WorkMachine]):
        self._chosen = chosen
        self._invalid = invalid

    def _assign_machine_cost(self,
                             job: jb.Job,
                             machine: wm.WorkMachine,
                             existing_jobs: List[jb.Job]) -> Optional[Tuple[float, List[jb.Job]]]:
        if machine in self._chosen:
            return (0.0, [])
        if machine in self._invalid:
            return None

        return (100.0, [])


class DefaultJobDistributionPolicyBaseTest(TestCase):
    def _get_machine(self, cpu: int, ram: int) -> wm.WorkMachine:
        return wm.WorkMachine("Test", wm.WorkMachineState.ONLINE,
                              wm.WorkMachineResources(cwm.ResourceAllocation(cpu, ram, 0)))

    def setUp(self) -> None:
        self._machines = [self._get_machine(10, 10), self._get_machine(5, 5), self._get_machine(1, 16)]
        self._job = _get_job(jb.JobPriority.MEDIUM, 0).job

    def test_no_suitable_machines(self) -> None:
        selector = DummyWorkMachineSelector([], self._machines)
        self.assertEqual(selector.assign_machine(job=_get_job(jb.JobPriority.MEDIUM, 0).job,
                         distribution=[], available_machines=self._machines), None)

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
