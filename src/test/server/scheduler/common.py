import datetime as dt

from copy import deepcopy
from ja.common.job import Job, JobPriority, JobSchedulingConstraints, JobStatus
from ja.common.docker_context import DockerConstraints
from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine, WorkMachineResources, WorkMachineState
from typing import Any, List
from unittest import TestCase

_global_job_counter: int = 0
_global_machine_counter: int = 0


def _datetime_before(since: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=since)


def get_job(prio: JobPriority,
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
              docker_context=None, docker_constraints=DockerConstraints(cpu, ram), status=status)

    job.uid = str(_global_job_counter)
    _global_job_counter += 1

    stats = JobRuntimeStatistics(_datetime_before(since), dt.datetime.now(), 0)
    return DatabaseJobEntry(job, stats, machine)


def get_machine(cpu: int, ram: int, swap: int = None) -> WorkMachine:
    global _global_machine_counter
    machine = WorkMachine("Test", WorkMachineState.ONLINE,
                          WorkMachineResources(ResourceAllocation(cpu, ram, swap if swap else ram)))
    machine.uid = str(_global_machine_counter)
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
