from ja.common.message.worker import WorkerResponse
from test.serializable.base import AbstractSerializableTest


class WorkerResponseTest(AbstractSerializableTest):
    """
    Class for testing WorkerResponse.
    """
    def setUp(self) -> None:
        self._optional_properties = ["uid"]
        self._object = WorkerResponse(result_string="SUCCESS", is_success=True, uid="job1")
        self._object_dict = {"result_string": "SUCCESS", "is_success": True, "uid": "job1"}
        self._other_object_dict = {"result_string": "FAILURE", "is_success": False, "uid": "job1"}
