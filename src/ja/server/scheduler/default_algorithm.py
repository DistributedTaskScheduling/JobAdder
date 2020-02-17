from copy import deepcopy
from ja.common.job import JobStatus, Job
from ja.common.work_machine import ResourceAllocation
from ja.server.database.database import ServerDatabase
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine
from ja.server.scheduler.algorithm import SchedulingAlgorithm, JobDistributionPolicy, CostFunction
from typing import List, Dict, Tuple


def get_allocation_for_job(job: Job, other_status: JobStatus = None) -> ResourceAllocation:
    """
    Get the resource allocation for a job depending on its status.
    """
    status = other_status if other_status else job.status
    if status is JobStatus.PAUSED:
        return ResourceAllocation(0, 0, job.docker_constraints.memory)
    return ResourceAllocation(job.docker_constraints.cpu_threads, job.docker_constraints.memory, 0)


class DefaultSchedulingAlgorithm(SchedulingAlgorithm):
    """
    The default scheduling algorithm used in JobAdder.
    """

    def __init__(self,
                 cost_function: CostFunction,
                 non_preemptive_distribution_policy: JobDistributionPolicy,
                 blocking_distribution_policy: JobDistributionPolicy,
                 preemptive_distribution_policy: JobDistributionPolicy):
        """!
        Initialize the scheduling algorithm.

          jobs. The list of jobs to be preempted returned by JobDistributionPolicy.assign_machine is ignored.
        @param blocking_distribution_policy The policy to use when choosing a machine to reserve for a blocking job.
          The list of jobs to be preempted returned by JobDistributionPolicy.assign_machine is ignored.
        @param preemptive_distribution_policy The policy to use when choosing a machine to reserve for a job which can
          preempt other jobs.
        """
        self._cost_func = cost_function
        self._non_preemptive_policy = non_preemptive_distribution_policy
        self._blocking_policy = blocking_distribution_policy
        self._preemptive_policy = preemptive_distribution_policy
        self._reserved_machines: Dict[str, str] = {}  # Job UID -> Machine UID
        self._cost_cache: Dict[str, float] = {}  # Job UID -> Effective cost

    def _set_state(self,
                   job: Job,
                   schedule: ServerDatabase.JobDistribution,
                   machine: WorkMachine,
                   new_status: JobStatus) -> None:
        if job.status in [JobStatus.RUNNING, JobStatus.PAUSED]:
            machine.resources.deallocate(get_allocation_for_job(job))

        job.status = new_status
        machine.resources.allocate(get_allocation_for_job(job))
        statistics: JobRuntimeStatistics = None
        for i in range(len(schedule)):
            if schedule[i].job.uid == job.uid:
                statistics = schedule[i].statistics
                del schedule[i]
                break
        schedule.append(DatabaseJobEntry(job, statistics, machine))

    def _free_machines(self, job: DatabaseJobEntry, next_machines: List[WorkMachine]) -> List[WorkMachine]:
        if self._cost_cache[job.job.uid] <= self._cost_func.preempting_threshold:
            return next_machines

        usable_machines = list(filter(lambda m: m.uid not in self._reserved_machines.values(), next_machines))
        if job.job.uid in self._reserved_machines:
            usable_machines += [m for m in next_machines if m.uid == self._reserved_machines[job.job.uid]]

        return usable_machines

    def _schedule_nonpreemptive(self,
                                job: DatabaseJobEntry,
                                next_schedule: ServerDatabase.JobDistribution,
                                next_machines: List[WorkMachine]) -> bool:
        # Try to schedule without preemption
        if job.job.status is JobStatus.PAUSED:
            # Special case: check that we have enough RAM and CPU
            need_allocation = get_allocation_for_job(job.job, JobStatus.RUNNING)
            if not job.assigned_machine.resources.allocate(need_allocation, test_only=True):
                return False
            self._set_state(job.job, next_schedule, job.assigned_machine, JobStatus.RUNNING)
            return True

        usable_machines = self._free_machines(job, next_machines)
        non_preemptive = self._non_preemptive_policy.assign_machine(job, next_schedule, usable_machines)
        if non_preemptive:
            self._set_state(job.job, next_schedule, non_preemptive[0], JobStatus.RUNNING)
            self._reserved_machines.pop(job.job.uid, None)  # Make sure we do not hold the reserved machine any longer
            return True
        return False

    def _schedule_blocking(self,
                           job: DatabaseJobEntry,
                           next_schedule: ServerDatabase.JobDistribution,
                           next_machines: List[WorkMachine]) -> None:
        result = self._blocking_policy.assign_machine(job, next_schedule, self._free_machines(job, next_machines))
        if result:
            self._reserved_machines[job.job.uid] = result[0].uid

    def _schedule_preemptive(self,
                             job: DatabaseJobEntry,
                             next_schedule: ServerDatabase.JobDistribution,
                             next_machines: List[WorkMachine]) -> bool:
        preemptive = self._preemptive_policy.assign_machine(job, next_schedule, self._free_machines(job, next_machines))
        if not preemptive:
            return False

        (machine, preempted_jobs) = preemptive
        for preempt in preempted_jobs:
            self._set_state(preempt, next_schedule, machine, JobStatus.PAUSED)
        self._set_state(job.job, next_schedule, machine, JobStatus.RUNNING)
        return True

    @staticmethod
    def _deepcopy_args(current_schedule: ServerDatabase.JobDistribution, available_machines: List[WorkMachine]) \
            -> Tuple[ServerDatabase.JobDistribution, List[WorkMachine]]:
        """
        Create a copy of the arguments, preserving jobs <-> workmachine mappings in the copies.
        """
        machines = deepcopy(available_machines)
        jobs: List[DatabaseJobEntry] = []
        for je in current_schedule:
            new_machine: WorkMachine = None
            if je.assigned_machine:
                new_machine = next(m for m in machines if m.uid == je.assigned_machine.uid)
            jobs.append(DatabaseJobEntry(deepcopy(je.job), deepcopy(je.statistics), new_machine))

        return (jobs, machines)

    def _compare_job_key(self, job: DatabaseJobEntry) -> Tuple[int, int, float]:
        is_job_preempting = 0 if self._cost_cache[job.job.uid] <= self._cost_func.preempting_threshold else 1
        is_job_paused = 0 if job.job.status == JobStatus.PAUSED else 1
        return (is_job_preempting, is_job_paused, self._cost_cache[job.job.uid])

    def reschedule_jobs(self,
                        current_schedule: ServerDatabase.JobDistribution,
                        available_machines: List[WorkMachine],
                        available_special_resources: Dict[str, int]) -> ServerDatabase.JobDistribution:
        # Copy machines and schedule first, so that we do not accidentally modify caller data
        (next_schedule, next_machines) = self._deepcopy_args(current_schedule, available_machines)

        # Update cached data
        for job in next_schedule:
            self._cost_cache[job.job.uid] = self._cost_func.calculate_cost(job)

        for job in sorted(next_schedule, key=self._compare_job_key):
            cost = self._cost_cache[job.job.uid]
            if job.job.status is JobStatus.RUNNING:
                # Nothing to do here
                continue

            next_special_resources = deepcopy(available_special_resources)
            if job.job.status is JobStatus.QUEUED:
                # Check whether we can schedule at all
                can_schedule = True
                for resource in job.job.scheduling_constraints.special_resources:
                    if resource not in next_special_resources or next_special_resources[resource] <= 0:
                        can_schedule = False
                    next_special_resources[resource] -= 1
                if not can_schedule:
                    continue

            if self._schedule_nonpreemptive(job, next_schedule, next_machines):
                available_special_resources = next_special_resources
                continue

            if cost <= self._cost_func.preempting_threshold:
                if self._schedule_preemptive(job, next_schedule, next_machines):
                    available_special_resources = next_special_resources
                    continue
                else:
                    break

            if cost <= self._cost_func.blocking_threshold:
                self._schedule_blocking(job, next_schedule, next_machines)

        return next_schedule
