from ja.common.job import JobSchedulingConstraints, JobPriority, Job
from ja.common.docker_context import DockerContext, DockerConstraints, MountPoint
from ja.common.message.worker_commands.start_job import StartJobCommand
from test.serializable.base import AbstractSerializableTest


class PauseJobCommandTest(AbstractSerializableTest):
    def setUp(self) -> None:
        self._optional_properties = []
        job = Job(
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
            label="thing"
        )
        self._object = StartJobCommand(job=job)
        self._object_dict = {
            "job": {
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
        }
        self._other_object_dict = {
            "job": {
                "status": 0,
                "owner_id": 1008,
                "email": "user@website.com",
                "scheduling_constraints": {"priority": 1, "is_preemptible": False, "special_resources": ["THING"]},
                "docker_context": {
                    "dockerfile_source": "ssh localhost",
                    "mount_points": []
                },
                "docker_constraints": {"cpu_threads": 4, "memory": 4096},
                "label": "thing"
            }
        }
