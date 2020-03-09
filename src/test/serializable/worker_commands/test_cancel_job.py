from ja.common.message.worker_commands.cancel_job import CancelJobCommand
from test.serializable.base import AbstractSerializableTest


class CancelJobCommandTest(AbstractSerializableTest):
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = CancelJobCommand(uid="job123")
        self._object_dict = {"uid": "job123"}
        self._other_object_dict = {"uid": "job456"}
