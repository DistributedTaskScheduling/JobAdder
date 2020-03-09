from ja.common.message.worker_commands.resume_job import ResumeJobCommand
from test.serializable.base import AbstractSerializableTest


class PauseJobCommandTest(AbstractSerializableTest):
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = ResumeJobCommand(uid="job123")
        self._object_dict = {"uid": "job123"}
        self._other_object_dict = {"uid": "job456"}
