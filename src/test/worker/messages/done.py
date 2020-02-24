from ja.common.docker_context import DockerContext, MountPoint, DockerConstraints
from ja.common.job import JobSchedulingConstraints, Job, JobStatus, JobPriority
from ja.server.database.sql.mock_database import MockDatabase
from test.serializable.base import AbstractSerializableTest
from ja.worker.message.done import JobDoneCommand


class DoneMessageTest(AbstractSerializableTest):

    def setUp(self) -> None:
        self.mock_db = MockDatabase()
        self.job: Job = Job(
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
        self.job.uid = "mrazqte"
        self.mock_db.update_job(self.job)
        self.job.status = JobStatus.QUEUED
        self.mock_db.update_job(self.job)
        self.job.status = JobStatus.RUNNING
        self.mock_db.update_job(self.job)
        self._optional_properties = []
        self._object = JobDoneCommand("52")
        self._object_dict = {"uid": "52"}
        self._other_object_dict = {"uid": "41"}

    def test_job_done(self) -> None:
        command = JobDoneCommand("mrazqte")
        command.execute(self.mock_db)
        self.assertEqual(self.mock_db.find_job_by_id("mrazqte").job.status, JobStatus.DONE)
