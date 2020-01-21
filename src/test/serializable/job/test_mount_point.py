from ja.common.docker_context import MountPoint
from test.serializable.base import AbstractSerializableTest


class MountPointTest(AbstractSerializableTest):
    """
    Class for testing MountPoint.
    """
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = MountPoint(source_path="/my/home/directory", mount_path="/unix/system/resources")
        self._object_dict = {"source_path": "/my/home/directory", "mount_path": "/unix/system/resources"}
        self._other_object_dict = {"source_path": "/opt/some/thing", "mount_path": "/opt/some/thing"}
