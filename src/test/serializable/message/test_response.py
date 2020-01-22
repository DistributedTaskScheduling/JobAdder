from ja.common.message.base import Response
from test.serializable.base import AbstractSerializableTest


class ResponseTest(AbstractSerializableTest):
    """
    Class for testing Response.
    """
    def setUp(self) -> None:
        self._optional_properties = []
        self._object = Response(result_string="SUCCESS", is_success=True)
        self._object_dict = {"result_string": "SUCCESS", "is_success": True}
        self._other_object_dict = {"result_string": "FAILURE", "is_success": False}
