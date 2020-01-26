import datetime as dt

from ja.common.job import Job, JobPriority, JobSchedulingConstraints, JobStatus
from ja.common.docker_context import DockerConstraints
from ja.common.work_machine import ResourceAllocation
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine, WorkMachineResources, WorkMachineState

_global_job_counter: int = 0
_global_machine_counter: int = 0


def _datetime_before(since: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=since)


def get_job(prio: JobPriority,
            since: int = 0,
            cpu: int = 1,
            ram: int = 1,
            machine: WorkMachine = None) -> DatabaseJobEntry:
    global _global_job_counter
    job = Job(owner_id=0, email="hey@you", scheduling_constraints=JobSchedulingConstraints(prio, False, []),
              docker_context=None, docker_constraints=DockerConstraints(cpu, ram))
    job.uid = str(_global_job_counter)
    _global_job_counter += 1
    job.status = JobStatus.QUEUED

    stats = JobRuntimeStatistics(_datetime_before(since), dt.datetime.now(), 0)
    return DatabaseJobEntry(job, stats, machine)


def get_machine(cpu: int, ram: int) -> WorkMachine:
    global _global_machine_counter
    machine = WorkMachine("Test", WorkMachineState.ONLINE,
                          WorkMachineResources(ResourceAllocation(cpu, ram, ram)))
    machine.uid = str(_global_machine_counter)
    _global_machine_counter += 1
    return machine
