from typing import List

from ja.common.job import Job, JobStatus
from ja.common.message.base import Response
from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from ja.common.message.worker_commands.pause_job import PauseJobCommand
from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from ja.common.message.worker_commands.start_job import StartJobCommand
from ja.common.proxy.ssh import SSHConfig, ISSHConnection
from ja.server.proxy.proxy import IWorkerProxy
from test.proxy.abstract import AbstractWorkerProxyTest


class WorkerProxyDummy(IWorkerProxy):
    def __init__(self, uid: str, jobs: List[Job]):
        self._uid = uid
        self._jobs: List[Job] = []
        for job in jobs:
            job_copy = Job.from_dict(job.to_dict())
            job_copy.status = JobStatus.RUNNING
            self._jobs.append(job_copy)

    def _get_remote_path(self) -> str:
        pass

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        pass

    def check_connection(self) -> None:
        pass

    def _find_job(self, uid: str) -> Job:
        for job in self._jobs:
            if job.uid == uid:
                return job
        return None

    @property
    def uid(self) -> str:
        return self._uid

    def dispatch_job(self, job: Job) -> Response:
        for existing_job in self._jobs:
            if job.uid == existing_job.uid:
                return Response.from_dict(Response(
                    result_string=StartJobCommand.RESPONSE_DUPLICATE % (job.uid, self.uid), is_success=False
                ).to_dict())
        job_copy = Job.from_dict(job.to_dict())
        job_copy._status = JobStatus.RUNNING
        self._jobs.append(job_copy)
        return Response.from_dict(Response(
            result_string=StartJobCommand.RESPONSE_SUCCESS % (job.uid, self.uid), is_success=True).to_dict())

    def cancel_job(self, uid: str) -> Response:
        for job in self._jobs:
            if uid == job.uid:
                job.status = JobStatus.CANCELLED
                self._jobs.remove(job)
                return Response.from_dict(Response(
                    result_string=CancelJobCommand.RESPONSE_SUCCESS % (uid, self.uid), is_success=True).to_dict())
        return Response.from_dict(Response(
            result_string=CancelJobCommand.RESPONSE_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())

    def pause_job(self, uid: str) -> Response:
        for job in self._jobs:
            if uid == job.uid:
                try:
                    job.status = JobStatus.PAUSED
                    return Response.from_dict(Response(
                        result_string=PauseJobCommand.RESPONSE_SUCCESS % (uid, self.uid), is_success=True).to_dict())
                except ValueError:
                    return Response.from_dict(Response(
                        result_string=PauseJobCommand.RESPONSE_NOT_RUNNING % (uid, self.uid), is_success=False
                    ).to_dict())
        return Response.from_dict(Response(
            result_string=PauseJobCommand.RESPONSE_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())

    def resume_job(self, uid: str) -> Response:
        for job in self._jobs:
            if uid == job.uid:
                try:
                    job.status = JobStatus.RUNNING
                    return Response.from_dict(Response(
                        result_string=ResumeJobCommand.RESPONSE_SUCCESS % (uid, self.uid), is_success=True).to_dict())
                except ValueError:
                    return Response.from_dict(Response(
                        result_string=ResumeJobCommand.RESPONSE_NOT_PAUSED % (uid, self.uid), is_success=False
                    ).to_dict())
        return Response.from_dict(Response(
            result_string=ResumeJobCommand.RESPONSE_UNKNOWN_JOB % (uid, self.uid), is_success=False).to_dict())


class WorkerProxyDummyTest(AbstractWorkerProxyTest):
    def setUp(self) -> None:
        super().setUp()
        self._empty_worker = WorkerProxyDummy(uid="empty-worker", jobs=[])
        self._busy_worker = WorkerProxyDummy(uid="busy-worker", jobs=[self._job_1, self._job_2])
