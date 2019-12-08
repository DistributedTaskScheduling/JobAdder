"""
Contains classes needed by each WC for providing a DockerClient as well
as notifying the CS
"""


class Worker:
    """
    The main class on the Worker Client
    """
    def __init__(self) -> None:
        """!
        Creates the DockerClient object used in this worker machine
        The configuration file will be read.
        The command handler should be created.
        The DockerEvents should be started
        """
