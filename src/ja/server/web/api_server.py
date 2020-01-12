from ja.server.database.database import ServerDatabase
from http.server import BaseHTTPRequestHandler


class WebRequestHandler(BaseHTTPRequestHandler):
    """!
    Handle a request to generate statistics.
    """

    def do_HEAD(self) -> None:
        """
        Handle an incoming HEAD request.
        """

    def do_GET(self) -> None:
        """
        Handle an incoming GET request.
        """


class StatisticsWebServer:
    """
    Creates a web server which enables external applications to obtain statistics about JobAdder.
    """

    def __init__(self, server_name: str, server_port: int, database: ServerDatabase):
        """!
        Initialize the web server.

        @param server_name server name for the server, see http.server.HTTPServer.
        @param server_port server port for the server, see http.server.HTTPServer.
        @param database The database to get information from when serving requests.
        """
