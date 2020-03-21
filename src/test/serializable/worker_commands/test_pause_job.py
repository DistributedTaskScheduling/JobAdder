from ja.common.message.worker_commands.pause_job import PauseJobCommand
from test.serializable.base import AbstractSerializableTest


class PauseJobCommandTest(AbstractSerializableTest):
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = PauseJobCommand(uid="job123")
        self._object_dict = {"uid": "job123"}
        self._other_object_dict = {"uid": "job456"}
