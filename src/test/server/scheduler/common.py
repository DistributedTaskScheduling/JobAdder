import datetime as dt

from copy import deepcopy
from ja.common.job import Job, JobPriority, JobSchedulingConstraints, JobStatus
from ja.common.docker_context import DockerConstraints, DockerContext, MountPoint
from ja.common.work_machine import ResourceAllocation
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine, WorkMachineResources, WorkMachineState
from typing import Any, List, Tuple
from unittest import TestCase

_global_job_counter: int = 0
_global_machine_counter: int = 0


def _datetime_before(since: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=since)


def get_job(prio: JobPriority = JobPriority.MEDIUM,
            since: int = 0,
            cpu: int = 1,
            ram: int = 1,
            machine: WorkMachine = None,
            status: JobStatus = JobStatus.QUEUED,
            user: int = 0,
            special_resources: List[str] = []) -> DatabaseJobEntry:
    global _global_job_counter
    job = Job(owner_id=user, email="hey@you",
              scheduling_constraints=JobSchedulingConstraints(prio, False, special_resources),
              docker_context=DockerContext("file", [MountPoint("adfsds", "jfaldsfj")]),
              docker_constraints=DockerConstraints(cpu, ram), status=status)

    job.uid = str(_global_job_counter)
    _global_job_counter += 1

    stats = JobRuntimeStatistics(_datetime_before(since), dt.datetime.now(), 0)
    return DatabaseJobEntry(job, stats, machine)


def get_scheduled_job(job: DatabaseJobEntry, machine: WorkMachine, next_status: JobStatus = None) -> DatabaseJobEntry:
    scheduled_job = DatabaseJobEntry(deepcopy(job.job), job.statistics, machine)
    if next_status:
        scheduled_job.job.status = next_status
    return scheduled_job


def get_machine(cpu: int, ram: int, swap: int = None) -> WorkMachine:
    global _global_machine_counter
    machine = WorkMachine("Test", WorkMachineState.ONLINE,
                          WorkMachineResources(ResourceAllocation(cpu, ram, swap if swap else ram)))
    machine.uid = str(_global_machine_counter)
    machine.ssh_config = SSHConfig(
        hostname="www.com", username="tux",
        password="1235", key_filename="~/my_key.rsa",
        passphrase="asdfgjk")
    _global_machine_counter += 1
    return machine


def assert_items_equal(self: TestCase, a: List[Any], b: List[Any]) -> None:
    b = deepcopy(b)
    self.assertEqual(len(a), len(b))
    for item in a:
        for i in range(len(b)):
            if item == b[i]:
                del b[i]
                break

    # If items are equal, then we erased all items from b (since len(a) == len(b) originally)
    self.assertEqual(len(b), 0)


def assert_distributions_equal(self: TestCase,
                               actual: ServerDatabase.JobDistribution,
                               expect: ServerDatabase.JobDistribution) -> None:
    def extract_info_job(job: DatabaseJobEntry) -> Tuple[str, JobStatus, str]:
        muid = job.assigned_machine.uid if job.assigned_machine else None
        return (job.job.uid, job.job.status, muid)

    actual_ids = [extract_info_job(job) for job in actual]
    expect_ids = [extract_info_job(job) for job in expect]
    assert_items_equal(self, actual_ids, expect_ids)
