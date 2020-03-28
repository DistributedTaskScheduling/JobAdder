from time import sleep

from ja.common.job import JobPriority
from test.integration.base import IntegrationTest


class SimpleIntegrationTest(IntegrationTest):
    """
    Simple test class that tests running jobs with 1 user client and 1 worker.
    """

    def test_add_one_job(self) -> None:
        client = self._clients[0]
        label = "not_a_bitcoin_miner"
        client.run(self.get_arg_list_add(num_seconds=2, label=label))

        active_job_entries = self._server._database.get_current_schedule()
        self.assertEqual(len(active_job_entries), 1)
        self.assertEqual(active_job_entries[0].job.label, label)

        containers_by_job_uid = self._workers[0]._docker_interface._containers_by_job_uid
        self.assertEqual(len(containers_by_job_uid), 1)

        sleep(4)

        active_job_entries = self._server._database.get_current_schedule()
        self.assertEqual(len(active_job_entries), 0)

        containers_by_job_uid = self._workers[0]._docker_interface._containers_by_job_uid
        self.assertEqual(len(containers_by_job_uid), 0)

    def test_scheduling_non_preemptive(self) -> None:
        client = self._clients[0]
        labels = ["medium-1", "medium-2", "medium-3", "low-1", "high-1"]
        client.run(self.get_arg_list_add(num_seconds=6, priority=JobPriority.MEDIUM, threads=1, label=labels[0]))
        client.run(self.get_arg_list_add(num_seconds=2, priority=JobPriority.MEDIUM, threads=1, label=labels[1]))
        client.run(self.get_arg_list_add(num_seconds=4, priority=JobPriority.MEDIUM, threads=2, label=labels[2]))
        client.run(self.get_arg_list_add(num_seconds=4, priority=JobPriority.LOW, threads=1, label=labels[3]))
        client.run(self.get_arg_list_add(num_seconds=2, priority=JobPriority.HIGH, threads=2, label=labels[4]))

        self._assert_current_schedule_as_expected(labels)
