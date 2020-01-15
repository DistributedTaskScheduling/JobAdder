from ja.common.job import JobSchedulingConstraints, JobPriority
from test.serializable.base import AbstractSerializableTest


class SchedulingConstraintsTest(AbstractSerializableTest):
    """
    Class for testing JobSchedulingConstraints.
    """
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = JobSchedulingConstraints(
            priority=JobPriority.HIGH, is_preemtible=True, special_resources=["SPESHUL", "Windows", "RPI4"]
        )
        self._object_dict = {
            "priority": 2, "is_preemptible": True, "special_resources": ["SPESHUL", "Windows", "RPI4"]
        }
        self._other_object_dict = {
            "priority": 3, "is_preemptible": True, "special_resources": ["SPESHUL", "Windows", "RPI4"]
        }
