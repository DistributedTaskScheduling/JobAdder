from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from test.server.scheduler.common import get_machine
from typing import Dict, Any
from unittest import TestCase

import ja.server.web.requests as req
import yaml


class AbstractWebRequestTest(TestCase):
    def setUp(self) -> None:
        self._db = MockDatabase()
        self._machine1 = get_machine(cpu=8, ram=8)
        self._machine1.resources.allocate(ResourceAllocation(8, 8, 4))
        self._machine2 = get_machine(cpu=16, ram=64)
        self._machine2.resources.allocate(ResourceAllocation(8, 8, 8))

        self._db.update_work_machine(self._machine1)
        self._db.update_work_machine(self._machine2)


class WorkMachineWorkloadTest(AbstractWebRequestTest):
    def _machine_info(self, m: WorkMachine) -> Dict[str, Any]:
        used = m.resources.total_resources - m.resources.free_resources
        free = m.resources.free_resources
        return {
            "id": m.uid,
            "cpu_load": {"used": used.cpu_threads, "free": free.cpu_threads},
            "memory_load": {"used": used.memory, "free": free.memory},
            "swap_space": {"used": used.swap, "free": free.swap},
        }

    def test_all_machines(self) -> None:
        request = req.WorkMachineWorkloadRequest()
        parsed_response = yaml.load(request.generate_report(self._db), Loader=yaml.SafeLoader)
        expected_response = {
            "machines": [
                self._machine_info(self._machine1),
                self._machine_info(self._machine2)
            ]
        }
        self.assertDictEqual(parsed_response, expected_response)
