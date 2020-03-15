import os
from unittest import TestCase
from copy import deepcopy
from time import sleep
from typing import Dict, cast

from ja.common.job import Job
from ja.worker.docker import DockerInterface
from test.worker.worker_server_proxy import WorkerServerProxyDummy

DOCKERFILE_SOURCE_1 = """
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 && apt-get clean

CMD ls
"""

DOCKERFILE_SOURCE_2 = """
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 && apt-get clean

CMD sleep 10
"""

DOCKERFILE_SOURCE_3 = """
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 && apt-get clean

CMD cat /var/tmp/input_file > /var/tmp/output_file
"""


class DockerInterfaceTest(TestCase):
    """
    Class for testing DockerInterface
    """
    def setUp(self) -> None:
        self._docker_interface = DockerInterface(server_proxy=WorkerServerProxyDummy(wmcs=dict(), jobs=dict()))
        self._mount_point_source_path = os.path.dirname(os.path.abspath(__file__)) + "/mount_directory/"
        generic_job_dict = {
            "status": 0,
            "owner_id": os.getuid(),
            "email": "user@website.com",
            "scheduling_constraints": {"priority": 1, "is_preemptible": False, "special_resources": ["THING"]},
            "docker_context": {
                "mount_points": [{"source_path": self._mount_point_source_path, "mount_path": "/var/tmp"}]
            },
            "docker_constraints": {"cpu_threads": 4, "memory": 4096},
            "label": "thing"
        }
        job_dict_1 = deepcopy(generic_job_dict)
        cast(Dict[str, object], job_dict_1["docker_context"])["dockerfile_source"] = DOCKERFILE_SOURCE_1
        self._job_1 = Job.from_dict(job_dict_1)
        job_dict_2 = deepcopy(generic_job_dict)
        cast(Dict[str, object], job_dict_2["docker_context"])["dockerfile_source"] = DOCKERFILE_SOURCE_2
        self._job_2 = Job.from_dict(job_dict_2)
        job_dict_3 = deepcopy(generic_job_dict)
        cast(Dict[str, object], job_dict_3["docker_context"])["dockerfile_source"] = DOCKERFILE_SOURCE_3
        self._job_3 = Job.from_dict(job_dict_3)

    def tearDown(self) -> None:
        # Remove output_file if it was created during the test:
        try:
            os.remove(self._mount_point_source_path + "output_file")
        except FileNotFoundError:
            pass

    def test_add_job(self) -> None:
        self._docker_interface.add_job(self._job_1)

    def test_cancel_job(self) -> None:
        self._docker_interface.add_job(self._job_2)
        self._docker_interface.cancel_job(self._job_2.uid)

    def test_pause_resume_job(self) -> None:
        self._docker_interface.add_job(self._job_2)
        self._docker_interface.pause_job(uid=self._job_2.uid)
        self._docker_interface.resume_job(uid=self._job_2.uid)

    def test_mount_point(self) -> None:
        self._docker_interface.add_job(self._job_3)
        sleep(0.1)  # Ensure that job has finished
        self.assertEqual(
            open(self._mount_point_source_path + "input_file", "r").read(),
            open(self._mount_point_source_path + "output_file", "r").read(),
        )
