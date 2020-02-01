from ja.common.job import JobPriority, JobStatus
from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from test.server.scheduler.common import get_job, get_machine
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
        self._machine2.resources.allocate(ResourceAllocation(8, 8, 0))

        self._job1 = get_job(JobPriority.LOW, cpu=8, ram=8, machine=self._machine1)
        self._job2 = get_job(JobPriority.MEDIUM, cpu=4, ram=4, machine=self._machine1)
        self._job2.job.status = JobStatus.RUNNING
        self._job2.job.status = JobStatus.PAUSED
        self._job3 = get_job(JobPriority.URGENT, cpu=8, ram=8, machine=self._machine2)
        self._job4 = get_job(JobPriority.HIGH)
        self._job4.job.status = JobStatus.RUNNING
        self._job4.job.status = JobStatus.DONE

        self._db.update_work_machine(self._machine1)
        self._db.update_work_machine(self._machine2)
        for job in [self._job1, self._job2, self._job3, self._job4]:
            self._db.update_job(job.job)
            self._db.assign_job_machine(job.job, job.assigned_machine)


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


class JobInformationTest(AbstractWebRequestTest):
    def _job_info(self, j: DatabaseJobEntry) -> Dict[str, Any]:
        return {
            "user_name": "root",
            "user_id": 0,
            "priority": j.job.scheduling_constraints.priority.name,
            "scheduled_at":
                self._db.find_job_by_id(j.job.uid).statistics.time_added.strftime(req.WebRequest.TIMESTAMP_FORMAT),
            "time_spent_running": j.statistics.running_time,
            "allocated_threads": j.job.docker_constraints.cpu_threads,
            "allocated_ram": j.job.docker_constraints.memory,
        }

    def test_existing_jobs(self) -> None:
        for job in [self._job1, self._job2, self._job3, self._job4]:
            request = req.JobInformationRequest(job.job.uid)
            response = yaml.load(request.generate_report(self._db), Loader=yaml.SafeLoader)
            self.assertDictEqual(response, self._job_info(job))

    def test_nonexisting_job(self) -> None:
        request = req.JobInformationRequest("abc")  # In our tests, job UIDs are only integers, so abc must be invalid
        error_dict = {"error": req.JobInformationRequest.NO_SUCH_JOB_TEMPLATE % "abc"}
        response = yaml.load(request.generate_report(self._db))
        self.assertDictEqual(error_dict, response)
