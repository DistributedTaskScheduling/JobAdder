from datetime import datetime
from freezegun import freeze_time  # type: ignore
from ja.server.database.database import ServerDatabase
from ja.server.web.api_server import WebRequestHandlerFactory, StatisticsWebServer
from unittest import TestCase
from unittest.mock import MagicMock

import ja.server.web.requests as req
import socket
import time


class MockBinaryIO:
    def __init__(self) -> None:
        self.data: str = ""

    def write(self, data: bytes) -> None:
        self.data += data.decode()


class MockRequest(req.WebRequest):
    def __init__(self, result: str):
        self._result = result

    def generate_report(self, database: ServerDatabase) -> str:
        return self._result


class WebRequestHandlerTest(TestCase):
    def setUp(self) -> None:
        self._handler = WebRequestHandlerFactory(database=None, mock_only=True)()
        self._handler.send_error = MagicMock()
        self._handler.send_response = MagicMock()
        self._handler.send_header = MagicMock()
        self._handler.end_headers = MagicMock()
        self._handler.wfile = MockBinaryIO()

    def test_invalid_path(self) -> None:
        # v2 is not implemented yet :)
        self.assertIsNone(self._handler.create_request_for_path("/v2/workmachines/workload"))
        self.assertIsNone(self._handler.create_request_for_path("/v1/admins"))
        self.assertIsNone(self._handler.create_request_for_path("/v1/jobs/hours/ab"))
        self.assertIsNone(self._handler.create_request_for_path("/v1/user//jobs"))

    def test_parse_correct_requests(self) -> None:
        workload_request = self._handler.create_request_for_path("/v1/workmachines/workload")
        self.assertIsInstance(workload_request, req.WorkMachineWorkloadRequest)

        job_info_request = self._handler.create_request_for_path("/v1/jobs/abc123")
        self.assertIsInstance(job_info_request, req.JobInformationRequest)
        self.assertEqual(job_info_request._job_uid, "abc123")

        user_jobs_request = self._handler.create_request_for_path("/v1/user/root/jobs")
        self.assertIsInstance(user_jobs_request, req.UserJobsRequest)
        self.assertEqual(user_jobs_request._user, "root")

        with freeze_time("2020-01-01 12:00:00"):
            past_jobs_request = self._handler.create_request_for_path("/v1/jobs/hours/6")
            self.assertIsInstance(past_jobs_request, req.PastJobsRequest)
            self.assertEqual(past_jobs_request._since, datetime(2020, 1, 1, 6, 0, 0))

        workmachine_jobs_request = self._handler.create_request_for_path("/v1/workmachines/123abc")
        self.assertIsInstance(workmachine_jobs_request, req.WorkMachineJobsRequest)
        self.assertEqual(workmachine_jobs_request._machine_id, "123abc")

    def test_respond_invalid_request(self) -> None:
        self._handler.do_response(request=None)
        self._handler.send_error.assert_called_once_with(404)
        self._handler.send_response.assert_not_called()
        self._handler.send_header.assert_not_called()
        self.assertEqual(self._handler.wfile.data, "")

    def _check_response(self, text: str) -> None:
        self._handler.do_response(request=MockRequest(text))
        self._handler.send_error.assert_not_called()
        self._handler.send_response.assert_called_once_with(200)
        self._handler.send_header.assert_called_once_with("Content-type", "application/x-yaml")
        self._handler.end_headers.assert_called_once()
        self.assertEqual(self._handler.wfile.data, text)

        # Reset state
        self._handler.wfile.data = ""
        self._handler.send_response.reset_mock()
        self._handler.send_header.reset_mock()
        self._handler.end_headers.reset_mock()

    def test_respond_valid_requests(self) -> None:
        self._check_response("{error: \"Invalid\"}")
        self._check_response("Hey! This is not a valid response but the request handler should not really care")


class StatisticsWebServerTest(TestCase):
    def test_server_starts(self) -> None:
        # Start server and wait for initialization
        server = StatisticsWebServer("127.0.0.1", 12345, None)
        time.sleep(1.0)

        # Check specified socket is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", 12345))
        self.assertEqual(result, 0)
        sock.close()

        # Clean up
        server.__del__()
