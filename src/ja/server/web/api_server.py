from ja.server.database.database import ServerDatabase
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Any

import ja.server.web.requests as req
import threading


def WebRequestHandlerFactory(database: ServerDatabase, mock_only: bool = False) -> type:
    class WebRequestHandler(BaseHTTPRequestHandler):
        """!
        Handle a request to generate statistics.
        """
        def __init__(self, *args: Any, **kwargs: Any):
            """
            Initialize the web request handler.

            @param database The database to use for request response data.
            """
            if not mock_only:
                super().__init__(*args, **kwargs)
            self._match_result: str = None

        def _check_match(self, path_parts: List[str], expect_parts: List[str]) -> bool:
            if len(path_parts) != len(expect_parts):
                return False

            for (given, expected) in zip(path_parts, expect_parts):
                if given == expected and expected != "*":
                    continue
                if expected != "*":
                    return False
                else:
                    self._match_result = given

            return True

        def create_request_for_path(self, path: str) -> req.WebRequest:
            """!
            Create an appropriate request depending on the requested path.

            @param path The requested path.
            """
            path_parts: List[str] = list(filter(None, path.split("/")))
            if self._check_match(path_parts, ["v1", "workmachines", "workload"]):
                return req.WorkMachineWorkloadRequest()
            elif self._check_match(path_parts, ["v1", "jobs", "*"]):
                return req.JobInformationRequest(self._match_result)
            elif self._check_match(path_parts, ["v1", "user", "*", "jobs"]):
                return req.UserJobsRequest(self._match_result)
            elif self._check_match(path_parts, ["v1", "jobs", "hours", "*"]):
                try:
                    return req.PastJobsRequest(int(self._match_result))
                except ValueError:
                    return None
            elif self._check_match(path_parts, ["v1", "workmachines", "*"]):
                return req.WorkMachineJobsRequest(self._match_result)
            else:
                return None

        def do_response(self, request: req.WebRequest) -> None:
            """
            Respond to the request.
            This means setting the appropriate headers, executing the request and send the requested data.

            @param request The request that was made, or None if invalid.
            """
            if not request:
                self.send_error(404)
                return

            self.send_response(200)
            self.send_header("Content-type", "application/x-yaml")
            self.end_headers()
            self.wfile.write(request.generate_report(database).encode())

        def do_GET(self) -> None:
            """
            Handle an incoming GET request.
            """
            self.do_response(self.create_request_for_path(self.path))
    return WebRequestHandler


class StatisticsWebServer:
    """
    Creates a web server which enables external applications to obtain statistics about JobAdder.
    """

    def _server_thread(self, server_name: str, server_port: int, database: ServerDatabase) -> None:
        try:
            self._server = HTTPServer((server_name, server_port), WebRequestHandlerFactory(database))
            self._server.timeout = 0.5  # Block for at most 0.5 seconds
            while not self._quit:
                self._server.handle_request()
            self._server.server_close()
        except Exception as e:
            print("Failed to start WebAPI server.")
            print(e)

    def __init__(self, server_name: str, server_port: int, database: ServerDatabase):
        """!
        Initialize the web server.

        @param server_name server name for the server, see http.server.HTTPServer.
        @param server_port server port for the server, see http.server.HTTPServer.
        @param database The database to get information from when serving requests.
        """
        self._quit = False
        self._thread = threading.Thread(target=self._server_thread, args=(server_name, server_port, database))
        self._thread.start()

    def __del__(self) -> None:
        if self._thread.is_alive():
            self._quit = True
            self._thread.join()
