from freezegun import freeze_time  # type: ignore
from ja.common.job import JobPriority, JobStatus
from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from test.server.scheduler.common import get_job, get_machine
from typing import Dict, Any, cast
from unittest import TestCase
from unittest.mock import MagicMock

import ja.server.web.requests as req
import pwd
import yaml


_pw_names = {
    0: "root",
    1: "daemon",
    2: "test"
}


class MockPwuid:
    def __init__(self, uid: int) -> None:
        global _pw_names
        self.pw_uid = uid
        self.pw_name = _pw_names[uid]


class MockPwnam:
    def __init__(self, user: str) -> None:
        global _pw_names
        if user not in _pw_names.values():
            raise KeyError("No such user")

        uid = 0
        for key in _pw_names:
            if _pw_names[key] == user:
                uid = key

        self.pw_uid = uid
        self.pw_name = user


class AbstractWebRequestTest(TestCase):
    def _add_job(self, *args: Any, **kwargs: Any) -> DatabaseJobEntry:
        job = get_job(*args, **kwargs)
        self._db.update_job(job.job)
        self._db.assign_job_machine(job.job, job.assigned_machine)
        return job

    def setUp(self) -> None:
        self._request: req.WebRequest = None
        self._db = MockDatabase()
        self._machine1 = get_machine(cpu=8, ram=8)
        self._machine1.resources.allocate(ResourceAllocation(8, 8, 4))
        self._machine2 = get_machine(cpu=16, ram=64)
        self._machine2.resources.allocate(ResourceAllocation(8, 8, 0))
        self._db.update_work_machine(self._machine1)
        self._db.update_work_machine(self._machine2)

        with freeze_time("2020-01-01 11:00:00"):
            self._job1 = self._add_job(JobPriority.LOW, cpu=8, ram=8, machine=self._machine1, user=0)
        with freeze_time("2020-01-01 10:00:00"):
            self._job2 = self._add_job(JobPriority.MEDIUM, cpu=4, ram=4, machine=self._machine1,
                                       user=0, status=JobStatus.QUEUED)
            self._job2.job.status = JobStatus.RUNNING
            self._db.update_job(self._job2.job)
            self._job2.job.status = JobStatus.PAUSED
            self._db.update_job(self._job2.job)
        with freeze_time("2020-01-01 09:00:00"):
            self._job3 = self._add_job(JobPriority.URGENT, cpu=8, ram=8, machine=self._machine2, user=2)
        with freeze_time("2020-01-01 00:00:00"):
            self._job4 = self._add_job(JobPriority.HIGH, since=0, status=JobStatus.DONE, user=0)

        pwd.getpwuid = MagicMock(side_effect=(lambda user: MockPwuid(user)))
        pwd.getpwnam = MagicMock(side_effect=(lambda user: MockPwnam(user)))

    def _do_report(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], yaml.load(self._request.generate_report(self._db), Loader=yaml.SafeLoader))


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
        self._request = req.WorkMachineWorkloadRequest()
        parsed_response = self._do_report()
        expected_response = {
            "machines": [
                self._machine_info(self._machine1),
                self._machine_info(self._machine2)
            ]
        }
        self.assertDictEqual(parsed_response, expected_response)


class JobInformationTest(AbstractWebRequestTest):
    def _job_info(self, j: DatabaseJobEntry) -> Dict[str, Any]:
        global _pw_names
        return {
            "user_name": _pw_names[j.job.owner_id],
            "user_id": j.job.owner_id,
            "priority": j.job.scheduling_constraints.priority.name,
            "scheduled_at":
                self._db.find_job_by_id(j.job.uid).statistics.time_added.strftime(req.WebRequest.TIMESTAMP_FORMAT),
            "time_spent_running": j.statistics.running_time,
            "allocated_threads": j.job.docker_constraints.cpu_threads,
            "allocated_ram": j.job.docker_constraints.memory,
        }

    def test_existing_jobs(self) -> None:
        for job in [self._job1, self._job2, self._job3, self._job4]:
            self._request = req.JobInformationRequest(job.job.uid)
            self.assertDictEqual(self._do_report(), self._job_info(job))

    def test_nonexisting_job(self) -> None:
        # In our tests, job UIDs are only integers, so abc must be invalid
        self._request = req.JobInformationRequest("abc")
        error_dict = {"error": req.JobInformationRequest.NO_SUCH_JOB_TEMPLATE % "abc"}
        self.assertDictEqual(error_dict, self._do_report())


class UserJobsTest(AbstractWebRequestTest):
    def test_user_jobs(self) -> None:
        user_jobs: Dict[int, Any] = {}
        user_jobs[0] = \
            {"jobs": [{"job_id": self._job1.job.uid}, {"job_id": self._job2.job.uid}, {"job_id": self._job4.job.uid}]}
        user_jobs[1] = {"jobs": []}  # User 1 should exist on all unix systems, but it is not guaranteed
        user_jobs[2] = {"jobs": [{"job_id": self._job3.job.uid}]}

        for user in range(3):
            self._request = req.UserJobsRequest(pwd.getpwuid(user).pw_name)
            self.assertDictEqual(user_jobs[user], self._do_report())

    def test_nonexisting_user(self) -> None:
        nonexisting_user = "xyz"
        self._request = req.UserJobsRequest(nonexisting_user)
        error_dict = {"error": req.UserJobsRequest.NO_SUCH_USER_TEMPLATE % nonexisting_user}
        self.assertDictEqual(error_dict, self._do_report())


class PastJobsTest(AbstractWebRequestTest):
    def test_no_jobs(self) -> None:
        with freeze_time("2020-01-01 12:00:00"):
            self._request = req.PastJobsRequest(0)
            self.assertDictEqual({"jobs": []}, self._do_report())

    def test_one_job(self) -> None:
        with freeze_time("2020-01-01 12:00:00"):
            self._request = req.PastJobsRequest(1)
            expect = {"jobs": [{"job_id": self._job1.job.uid}]}
            self.assertDictEqual(expect, self._do_report())

    def test_all_jobs(self) -> None:
        with freeze_time("2020-01-01 12:00:00"):
            self._request = req.PastJobsRequest(12)
            expect = {"jobs": [{"job_id": self._job1.job.uid}, {"job_id": self._job2.job.uid},
                               {"job_id": self._job3.job.uid}, {"job_id": self._job4.job.uid}]}
            self.assertDictEqual(expect, self._do_report())


class WorkMachineJobsTest(AbstractWebRequestTest):
    def test_empty_machine(self) -> None:
        machine3 = get_machine(cpu=1, ram=1)
        self._db.update_work_machine(machine3)
        self._request = req.WorkMachineJobsRequest(machine3.uid)
        self.assertDictEqual({"jobs": []}, self._do_report())

    def test_nonexisting_machine(self) -> None:
        self._request = req.WorkMachineJobsRequest("xyz")
        self.assertDictEqual({"error": req.WorkMachineJobsRequest.NO_SUCH_MACHINE_TEMPLATE % "xyz"}, self._do_report())

    def test_machine1(self) -> None:
        expect = {"jobs": [{"job_id": self._job1.job.uid}, {"job_id": self._job2.job.uid}]}
        self._request = req.WorkMachineJobsRequest(self._machine1.uid)
        self.assertDictEqual(expect, self._do_report())

    def test_machine2(self) -> None:
        expect = {"jobs": [{"job_id": self._job3.job.uid}]}
        self._request = req.WorkMachineJobsRequest(self._machine2.uid)
        self.assertDictEqual(expect, self._do_report())
