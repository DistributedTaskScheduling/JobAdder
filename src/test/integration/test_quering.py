from time import sleep

from test.integration.base import IntegrationTest
from typing import List
from io import StringIO
from unittest.mock import patch


class QueryIntegrationTest(IntegrationTest):
    """
    Test that test querying a job that has finished.
    """

    def _get_arg_list_query(self) -> List[str]:
        arg_list = [
            "--hostname", "127.0.0.1",
            "-v", "2",
            "query",
            "--status", "done",
            "--label", "not_a_bitcoin_miner"
        ]
        return arg_list

    def test_query_one_job(self) -> None:
        client = self._clients[0]
        label = "not_a_bitcoin_miner"
        client.run(self.get_arg_list_add(num_seconds=2, label=label))
        client.run(self.get_arg_list_add(num_seconds=2, label="123"))
        sleep(4)
        with patch("sys.stdout", new=StringIO()) as fakeOutput:
            client.run(self._get_arg_list_query())
            queried_jobs = self._server._database.find_job_by_label("not_a_bitcoin_miner")[0]
            self.assertEqual(fakeOutput.getvalue().strip() + "\n", str(queried_jobs))
