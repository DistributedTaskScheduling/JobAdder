import datetime as dt
import ja.common.job as jb
import ja.server.database.types.job_entry as je
import ja.server.scheduler.default_policies as dp
from unittest import TestCase


class DefaultCostFunctionTest(TestCase):
    def setUp(self) -> None:
        self.cost_func = dp.DefaultCostFunction()
        self.low_base = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.LOW, 0))
        self.medium_base = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.MEDIUM, 0))
        self.high_base = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.HIGH, 0))
        self.urgent_base = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.URGENT, 0))

    def _datetime_before(self, since: int) -> dt.datetime:
        return dt.datetime.now() - dt.timedelta(minutes=since)

    def _get_job(self, prio: jb.JobPriority, since: int) -> je.DatabaseJobEntry:
        job = jb.Job(owner_id=0, email="hey@you", scheduling_constraints=jb.JobSchedulingConstraints(prio, False, []),
                     docker_context=None, docker_constraints=None)
        stats = je.JobRuntimeStatistics(self._datetime_before(since), dt.datetime.now(), 0)
        return je.DatabaseJobEntry(job, stats, None)

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
        after_5_mins = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.MEDIUM, 5))
        after_15_mins = self.cost_func.calculate_cost(self._get_job(jb.JobPriority.MEDIUM, 15))
        self.assertLessEqual(after_15_mins, after_5_mins)
        self.assertLessEqual(after_5_mins, self.medium_base)

    def test_preempt_after_block(self) -> None:
        self.assertLessEqual(self.cost_func.preempting_threshold, self.cost_func.blocking_threshold)
