from ja.common.docker_context import DockerConstraints
from test.serializable.base import AbstractSerializableTest


class DockerConstraintsTest(AbstractSerializableTest):
    """
    Class for testing DockerConstraints.
    """
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = DockerConstraints(cpu_threads=-1, memory=1024)
        self._object_dict = {"cpu_threads": -1, "memory": 1024}
        self._other_object_dict = {"cpu_threads": 4, "memory": 1024}
