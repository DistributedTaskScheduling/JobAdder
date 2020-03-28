from time import sleep

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

    def test_sanity_checks(self) -> None:
        work_machines = self._server._database.get_work_machines()
        self.assertEqual(len(work_machines), self.num_workers)
        for i in range(self.num_workers):
            worker_i_exists = False
            for work_machine in work_machines:
                if work_machine.uid == "worker_%s" % i:
                    worker_i_exists = True
                    break
            self.assertTrue(worker_i_exists, "Worker %s does not exist." % i)

    def test_no_user_cli_args(self) -> None:
        self._clients[0].run(cli_args=[], suppress_help=True)  # Assure that the program doesn't just crash
