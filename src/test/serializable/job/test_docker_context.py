from ja.common.docker_context import DockerContext, MountPoint
from test.serializable.base import AbstractSerializableTest


class DockerContextTest(AbstractSerializableTest):
    """
    Class for testing DockerContext.
    """
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = DockerContext(
            dockerfile_source="sudo apt install docker",
            mount_points=[
                MountPoint(source_path="/home/user", mount_path="/home/user"),
                MountPoint(source_path="/opt/thing", mount_path="/opt/THING")
            ]
        )
        self._object_dict = {
            "dockerfile_source": "sudo apt install docker",
            "mount_points": [
                {"source_path": "/home/user", "mount_path": "/home/user"},
                {"source_path": "/opt/thing", "mount_path": "/opt/THING"}
            ]
        }
        self._other_object_dict = {
            "dockerfile_source": "sudo apt install docker",
            "mount_points": [
                {"source_path": "/home/user", "mount_path": "/home/user"},
            ]
        }
