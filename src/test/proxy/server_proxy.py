from ja.user.proxy import IUserServerProxy
from ja.common.message.server import ServerResponse
from ja.common.job import Job, JobStatus, JobPriority

from ja.user.message.add import AddCommand
from ja.user.message.query import QueryCommand
from ja.user.message.cancel import CancelCommand
from typing import List, Tuple
import copy
from datetime import datetime


class ServerProxyDummy(IUserServerProxy):

    def __init__(self, jobs: List[Job]):
        self._jobs = copy.deepcopy(jobs)
        self._counter = 0

    @property
    def jobs(self) -> List[Job]:
        """
        @return: the jobs on the server.
        """
        return self._jobs

    def add_job(self, add_command: AddCommand) -> ServerResponse:
        add_config = add_command.config
        job: Job = add_config.job
        if job in self._jobs:
            return ServerResponse(result_string="Job with id %s already exists" % job.uid,
                                  is_success=False)
        job.uid = str(self._counter)
        self._counter += 1
        self._jobs.append(job)
        job.status = JobStatus.QUEUED
        return ServerResponse(result_string="Successfully added job with id: %s" % job.uid,
                              is_success=True)

    def cancel_job(self, cancel_command: CancelCommand) -> ServerResponse:
        job_uid: str = cancel_command.uid
        job_label: str = cancel_command.label
        if job_uid is not None:
            for job in self._jobs:
                if job.uid == job_uid:
                    if False:  # TODO: Find a way to verify if this is the owner
                        return ServerResponse(result_string="You do not have the permission to cancel the"
                                                            "job with id %s" % job_uid,
                                              is_success=False)
                    job.status = JobStatus.CANCELLED
                    return ServerResponse(result_string="Successfully removed job with id: %s" % job_uid,
                                          is_success=True)
            return ServerResponse(result_string="Job with id %s does not exist!" % job_uid,
                                  is_success=False)

        if job_label is not None:
            for job in self._jobs:
                if job.label == job_label:
                    if False:  # TODO
                        return ServerResponse(result_string="You do not have the permission to cancel the"
                                                            "job with label %s" % job_label,
                                              is_success=False)
                    job.status = JobStatus.CANCELLED
                    print(job.status)
                    return ServerResponse(result_string="Successfully removed job with label: %s" % job_label,
                                          is_success=True)
            return ServerResponse(result_string="Job with label %s does not exist!" % job_label,
                                  is_success=False)
        return None

    def query(self, query_command: QueryCommand) -> List[Job]:
        # Load parameters
        uid: List[str] = query_command.uid
        label: List[str] = query_command.label
        owner: List[str] = query_command.owner
        priority: List[JobPriority] = query_command.priority
        status: List[JobStatus] = query_command.status
        is_preemptible: bool = query_command.is_preemptible
        special_resources: List[List[str]] = query_command.special_resources
        cpu_threads: Tuple[int, int] = query_command.cpu_threads
        memory: Tuple[int, int] = query_command.memory
        before: datetime = query_command.before
        after: datetime = query_command.after

        result: List[Job] = copy.deepcopy(self._jobs)
        # Gradually remove all jobs that do not satisfy the querying constraints.
        i = 0
        while i < len(result):
            job = result[i]
            if before is not None:
                if job.added > before:
                    del result[i]
                    continue
            if after is not None:
                if job.added < after:
                    del result[i]
                    continue
            if uid is not None:
                if job.uid not in uid:
                    del result[i]
                    continue
            if label is not None:
                if job.label not in label:
                    del result[i]
                    continue
            if owner is not None:
                if job.owner_id not in owner:
                    del result[i]
                    continue
            if priority is not None:
                if job.scheduling_constraints.priority not in priority:
                    del result[i]
                    continue
            if status is not None:
                if job.status not in status:
                    del result[i]
                    continue
            if is_preemptible is not None:
                if job.scheduling_constraints.is_preemptible != is_preemptible:
                    del result[i]
                    continue
            if special_resources is not None:
                if job.scheduling_constraints.special_resources not in special_resources:
                    del result[i]
                    continue
            if cpu_threads is not None:
                job_cpu: int = job.docker_constraints.cpu_threads
                if job_cpu < cpu_threads[0] or job_cpu > cpu_threads[1]:
                    del result[i]
                    continue
            if memory is not None:
                job_mem: int = job.docker_constraints.memory
                if job_mem < memory[0] or job_mem > memory[1]:
                    del result[i]
                    continue
            i += 1

        # message: str = ""
        # for job in result:
        #    message += str(job) + ", "
        # if message == "":
        #    message = "No jobs satisfy these constraints."
        return result  # ServerResponse(message, is_success=True)
