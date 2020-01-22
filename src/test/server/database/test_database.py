from unittest import TestCase
from datetime import datetime, timedelta
from ja.common.work_machine import ResourceAllocation
from ja.server.database.sql.mock_database import MockDatabase
from ja.common.job import Job, JobSchedulingConstraints, JobPriority, JobStatus
from ja.common.docker_context import DockerContext, MountPoint, DockerConstraints
from ja.server.database.types.work_machine import WorkMachine, WorkMachineState, WorkMachineResources
import time


class DatabaseTest(TestCase):
    """
    Class for testing Database.
    """

    def setUp(self) -> None:
        self.mockDatabase = MockDatabase()
        self.job: Job = Job(
            owner_id=1008,
            email="user@website.com",
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=False, special_resources=["THING"]
            ),
            docker_context=DockerContext(
                dockerfile_source="ssh localhost",
                mount_points=[MountPoint(source_path="/home/user", mount_path="/home/user")]
            ),
            docker_constraints=DockerConstraints(cpu_threads=4, memory=4096),
            label="thig"
        )

        self.job.uid = "asv"

        self.job2: Job = Job(
            owner_id=1008,
            email="website.com",
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=False, special_resources=["THING"]
            ),
            docker_context=DockerContext(
                dockerfile_source="ssh localhost",
                mount_points=[MountPoint(source_path="/home/user", mount_path="/home/user")]
            ),
            docker_constraints=DockerConstraints(cpu_threads=4, memory=4096),
            label="thing"
        )
        self.job2.uid = "asv"
        self.work_machine = WorkMachine("machi1", WorkMachineState.ONLINE,
                                        WorkMachineResources(ResourceAllocation(12, 32, 12)))
        self.work_machine2 = WorkMachine("machi2", WorkMachineState.ONLINE,
                                         WorkMachineResources(ResourceAllocation(2, 2, 2)))

    def test_insert_job(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.assertTrue(self.job == self.job)

    # test update same object
    def test_update_job1(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.job.email = "new@email"
        self.mockDatabase.update_job(self.job)
        self.job.label = "newlabel"
        self.mockDatabase.update_job(self.job)
        self.job.email = "ps"
        new_job = self.mockDatabase.find_job_by_id(self.job.uid).job
        self.assertTrue(new_job.email == "new@email")
        self.assertTrue(new_job.label == "newlabel")

    # test update with different object but same uid
    def test_update_job2(self) -> None:
        # add job to the database
        self.mockDatabase.update_job(self.job)
        # update with job2
        self.job2.status = JobStatus.QUEUED
        self.mockDatabase.update_job(self.job2)
        self.job2.status = JobStatus.RUNNING
        self.mockDatabase.update_job(self.job2)
        self.assertTrue(self.mockDatabase.find_job_by_id(self.job2.uid).job == self.job2)
        self.assertFalse(self.mockDatabase.find_job_by_id(self.job2.uid).job == self.job)

    def test_update_job_running_time(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.job.status = JobStatus.QUEUED
        self.job.status = JobStatus.RUNNING
        self.mockDatabase.update_job(self.job)
        time.sleep(1)
        self.job.status = JobStatus.PAUSED
        self.mockDatabase.update_job(self.job)
        time.sleep(1)
        self.job.status = JobStatus.RUNNING
        self.mockDatabase.update_job(self.job)
        time.sleep(1)
        self.job.status = JobStatus.DONE
        self.mockDatabase.update_job(self.job)
        j_entry = self.mockDatabase.find_job_by_id(self.job.uid)
        self.assertTrue(j_entry.statistics.paused_time == 1)
        self.assertTrue(j_entry.statistics.running_time == 2)

    def test_get_job_entry_running_type(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.job.status = JobStatus.QUEUED
        self.job.status = JobStatus.RUNNING
        self.mockDatabase.update_job(self.job)
        time.sleep(1)
        j_entry = self.mockDatabase.find_job_by_id(self.job.uid)
        self.assertEqual(j_entry.statistics.running_time, 1)

    def test_start_time(self) -> None:
        self.job2.status = JobStatus.QUEUED
        self.job2.status = JobStatus.RUNNING
        # add job to the database
        self.mockDatabase.update_job(self.job)
        # update with job2
        self.mockDatabase.update_job(self.job2)
        job_entry = self.mockDatabase.find_job_by_id(self.job2.uid)
        self.assertFalse(job_entry.statistics.time_started is None)
        self.assertFalse(job_entry.statistics.time_added == job_entry.statistics.time_started)

    def test_from_dict_to_database(self) -> None:
        object_dict = {
            "uid": "bc",
            "status": 0,
            "owner_id": 1008,
            "email": "user@website.com",
            "scheduling_constraints": {"priority": 1, "is_preemptible": False, "special_resources": ["THING"]},
            "docker_context": {
                "dockerfile_source": "ssh localhost",
                "mount_points": [{"source_path": "/home/user", "mount_path": "/home/user"}]
            },
            "docker_constraints": {"cpu_threads": 4, "memory": 4096},
            "label": "thing"
        }
        job3 = Job.from_dict(object_dict)
        self.mockDatabase.update_job(job3)
        self.assertEqual(job3, self.mockDatabase.find_job_by_id(job3.uid).job)

    def test_update_work_machine(self) -> None:
        self.mockDatabase.update_work_machine(self.work_machine)
        self.assertEqual(self.mockDatabase.get_work_machines()[0], self.work_machine)
        work_machine2 = WorkMachine("machi1", WorkMachineState.OFFLINE,
                                    WorkMachineResources(ResourceAllocation(12, 32, 12)))
        self.mockDatabase.update_work_machine(work_machine2)
        self.assertEqual(self.mockDatabase.get_work_machines()[0], work_machine2)

    def test_assign_job_machine(self) -> None:
        self.mockDatabase.update_work_machine(self.work_machine)
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.assign_job_machine(self.job, self.work_machine)
        self.assertEqual(self.mockDatabase.get_jobs_on_machine(self.work_machine), [self.job])

    def test_schedule(self) -> None:
        self.job2.status = JobStatus.QUEUED
        self.job2.status = JobStatus.CANCELLED
        self.job2.uid = "job2"
        self.job.status = JobStatus.QUEUED
        self.mockDatabase.update_job(self.job)
        self.job.status = JobStatus.RUNNING
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.update_job(self.job2)
        schedule = self.mockDatabase.get_current_schedule()
        self.assertEqual(schedule, [self.mockDatabase.find_job_by_id(self.job.uid)])

    def test_query_jobs(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.update_work_machine(self.work_machine)
        self.mockDatabase.assign_job_machine(self.job, self.work_machine)
        jobs = self.mockDatabase.query_jobs((datetime.now() - timedelta(hours=12)), 1008, self.work_machine)
        self.assertEqual(jobs, [self.mockDatabase.find_job_by_id(self.job.uid)])
        jobs = self.mockDatabase.query_jobs(None, 108, self.work_machine)
        self.assertNotEqual(jobs, [self.mockDatabase.find_job_by_id(self.job.uid)])

    def test_query_jobs_no_wm(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.update_work_machine(self.work_machine)
        self.mockDatabase.assign_job_machine(self.job, self.work_machine)
        self.job2.uid = "abc"
        self.mockDatabase.update_job(self.job2)
        self.mockDatabase.update_work_machine(self.work_machine2)
        self.mockDatabase.assign_job_machine(self.job2, self.work_machine2)
        jobs = self.mockDatabase.query_jobs(None, 1008, None)
        self.assertEqual(
            jobs, [self.mockDatabase.find_job_by_id(self.job.uid), self.mockDatabase.find_job_by_id(self.job2.uid)])

    def test_query_jobs_no_owner_id(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.update_work_machine(self.work_machine)
        self.mockDatabase.assign_job_machine(self.job, self.work_machine)
        self.job2.uid = "abc"
        self.job2.owner_id = 44
        self.mockDatabase.update_job(self.job2)
        self.mockDatabase.assign_job_machine(self.job2, self.work_machine)
        jobs = self.mockDatabase.query_jobs(None, -1, self.work_machine)
        self.assertEqual(
            jobs, [self.mockDatabase.find_job_by_id(self.job.uid), self.mockDatabase.find_job_by_id(self.job2.uid)])

    def test_query_jobs_false(self) -> None:
        self.mockDatabase.update_job(self.job)
        self.mockDatabase.update_work_machine(self.work_machine)
        self.mockDatabase.assign_job_machine(self.job, self.work_machine)
        self.job2.uid = "abc"
        self.job2.owner_id = 12
        self.mockDatabase.update_job(self.job2)
        self.mockDatabase.update_work_machine(self.work_machine2)
        self.mockDatabase.assign_job_machine(self.job2, self.work_machine2)
        jobs = self.mockDatabase.query_jobs(None, 1008, None)
        self.assertNotEqual(
            jobs, [self.mockDatabase.find_job_by_id(self.job.uid), self.mockDatabase.find_job_by_id(self.job2.uid)])

        jobs = self.mockDatabase.query_jobs(None, -1, self.work_machine)
        self.assertEqual(jobs, [self.mockDatabase.find_job_by_id(self.job.uid)])
