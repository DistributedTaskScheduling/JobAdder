from ja.common.docker_context import DockerContext, MountPoint, DockerConstraints
from ja.common.job import JobSchedulingConstraints, JobPriority, Job
from ja.common.proxy.ssh import SSHConfig
from test.serializable.base import AbstractSerializableTest
from typing import List

from ja.user.config.add import AddCommandConfig
from ja.user.config.base import UserConfig
from ja.user.config.base import Verbosity


class AddCommandConfigTest(AbstractSerializableTest):
    """
    Class for testing AddCommandConfig
    """

    def setUp(self) -> None:
        config = UserConfig(
            ssh_config=SSHConfig(
                hostname="ies", username="pettto", password="1234567890", key_filename="~/.ssh/id_rsa"),
            verbosity=Verbosity.DETAILED)
        self._object = AddCommandConfig(config=config,
                                        job=Job(
                                            owner_id=1008,
                                            email="user@website.com",
                                            scheduling_constraints=JobSchedulingConstraints(
                                                priority=JobPriority.MEDIUM, is_preemptible=False,
                                                special_resources=["THING"]
                                            ),
                                            docker_context=DockerContext(
                                                dockerfile_source="ssh localhost",
                                                mount_points=[
                                                    MountPoint(source_path="/home/user", mount_path="/home/user")]
                                            ),
                                            docker_constraints=DockerConstraints(cpu_threads=4, memory=4096),
                                            label="thing"
                                        ),
                                        blocking=False)
        v_list: List[str] = list(AddCommandConfig.__dir__(self._object))
        self._optional_properties = [a[1:] for a in v_list]
        self._object_dict = {
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "ies",
                    "username": "pettto",
                    "password": "1234567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            },
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
            },
            "blocking": False
        }
        self._other_object_dict = {
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "ies",
                    "username": "peto",
                    "password": "1234567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            },
            "job": {
                "status": 0,
                "owner_id": 100,
                "email": "user@webste.com",
                "scheduling_constraints": {"priority": 1, "is_preemptible": False, "special_resources": ["THING"]},
                "docker_context": {
                    "dockerfile_source": "ssh localhost",
                    "mount_points": [{"source_path": "/home/user", "mount_path": "/home/user"}]
                },
                "docker_constraints": {"cpu_threads": 4, "memory": 4096},
                "label": "thing"
            },
            "blocking": True
        }
