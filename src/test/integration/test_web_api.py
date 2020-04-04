from ja.server.config import ServerConfig
from test.integration.base import IntegrationTest
from typing import Any, Dict, cast
from getpass import getuser

import requests
import yaml


class TestWebAPI(IntegrationTest):
    def run_query(self, url: str, expect_code: int, expect_content: Dict[str, Any] = {}) -> None:
        query = requests.get("http://127.0.0.1:12345/" + url)
        self.assertEqual(query.status_code, expect_code)
        if expect_code == 200:
            response = cast(Dict[str, object], yaml.load(query.content, Loader=yaml.SafeLoader))
            self.assertDictEqual(response, expect_content)

    def test_web_api(self) -> None:
        """
        A test where a worker and 2 jobs are added, then basic checks are made via the WebAPI.
        """
        self._clients[0].run(
            self.get_arg_list_add(num_seconds=60, label="lo", priority="0", threads=4, memory=16 * 1024))
        self._clients[1].run(
            self.get_arg_list_add(num_seconds=60, label="me", priority="1", threads=4, memory=16 * 1024))

        self.run_query("v1/invalid", 404)

        jobs = self._server._database.query_jobs(None, -1, None)
        machine = self._server._database.get_work_machines()[0]

        jobs_uid_dict = {"jobs": [{"job_id": job.job.uid} for job in jobs]}
        self.run_query("v1/user/%s/jobs" % getuser(), 200, jobs_uid_dict)

        workload = {
            "machines": [{
                "id": machine.uid,
                "cpu_load": {"used": 4, "free": 0},
                "memory_load": {"used": 16 * 1024, "free": 0},
                "swap_space": {"used": 0, "free": 16 * 1024},
            }]
        }
        self.run_query("v1/workmachines/workload", 200, workload)

    @property
    def server_config(self) -> ServerConfig:
        cfg = super().server_config
        cfg._web_server_port = 12345
        return cfg

    @property
    def num_workers(self) -> int:
        return 1

    @property
    def num_clients(self) -> int:
        return 2
