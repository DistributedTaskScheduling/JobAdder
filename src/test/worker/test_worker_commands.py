from unittest import TestCase

from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from ja.common.message.worker_commands.pause_job import PauseJobCommand
from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from ja.common.message.worker_commands.start_job import StartJobCommand
from ja.worker.docker import DockerInterface
from ja.common.job import Job, JobStatus, JobPriority, JobSchedulingConstraints
from ja.common.docker_context import DockerContext, DockerConstraints
from test.worker.test_docker_interface import DOCKERFILE_SOURCE_1, DOCKERFILE_SOURCE_2


class WorkerCommandTest(TestCase):
    def setUp(self) -> None:
        self._docker_interface = DockerInterface(server_proxy=None, worker_uid="worker")
        self._uid_1 = "job-1"
        self._job_1 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source=DOCKERFILE_SOURCE_1, mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_1.uid = self._uid_1
        self._job_1.status = JobStatus.QUEUED
        self._uid_2 = "job-2"
        self._job_2 = Job(
            owner_id=1003,
            email=None,
            scheduling_constraints=JobSchedulingConstraints(
                priority=JobPriority.MEDIUM, is_preemptible=True, special_resources=[]
            ),
            docker_context=DockerContext(dockerfile_source=DOCKERFILE_SOURCE_2, mount_points=[]),
            docker_constraints=DockerConstraints(cpu_threads=1, memory=1024)
        )
        self._job_2.uid = self._uid_2
        self._job_2.status = JobStatus.QUEUED
        self._uid_unknown = "DEADBEEF"

    def test_start_job(self) -> None:
        command = StartJobCommand(job=self._job_1)
        response = command.execute(self._docker_interface)
        self.assertTrue(response.is_success)
        response_duplicate = command.execute(self._docker_interface)
        self.assertFalse(response_duplicate.is_success)

    def test_cancel_job(self) -> None:
        self._docker_interface.add_job(self._job_2)
        command = CancelJobCommand(self._uid_2)
        response = command.execute(self._docker_interface)
        self.assertTrue(response.is_success)
        response_unknown_job = command.execute(self._docker_interface)
        self.assertFalse(response_unknown_job.is_success)

    def test_pause_resume_job(self) -> None:
        self._docker_interface.add_job(self._job_2)
        command_pause = PauseJobCommand(self._uid_2)
        command_resume = ResumeJobCommand(self._uid_2)
        response_pause = command_pause.execute(self._docker_interface)
        self.assertTrue(response_pause.is_success)
        response_already_paused = command_pause.execute(self._docker_interface)
        self.assertFalse(response_already_paused.is_success)
        response_resume = command_resume.execute(self._docker_interface)
        self.assertTrue(response_resume.is_success)
        response_already_resumed = command_resume.execute(self._docker_interface)
        self.assertFalse(response_already_resumed.is_success)

        command_pause_unknown = PauseJobCommand(self._uid_unknown)
        response_pause_unknown = command_pause_unknown.execute(self._docker_interface)
        self.assertFalse(response_pause_unknown.is_success)
        command_resume_unknown = ResumeJobCommand(self._uid_unknown)
        response_resume_unknown = command_resume_unknown.execute(self._docker_interface)
        self.assertFalse(response_resume_unknown.is_success)
