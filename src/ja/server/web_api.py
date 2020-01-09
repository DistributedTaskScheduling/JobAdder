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

    def __init__(self, host: str, port: int, database: ServerDatabase):
        """!
        Initialize the web server.

        @param host The host for the server.
        @param port The port for the server.
        @param database The database to get information from when serving requests.
        """
