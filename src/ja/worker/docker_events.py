"""
This module is responsible for the monitoring of the docker containers
running on the worker machine.
"""
from typing import Dict


class DockerEvents:
    """
    Monitors the containers on the current machine
    """

    def __init__(self) -> None:
        """!
        Starts the event loop
        that will be monitoring the state of the containers.
        """

    def change_filters(self, filters: Dict[str, str]) -> None:
        """!
        Change on which events the server is going to be notified
        @param filters: filter the events by event time, container or image
            filters and events are described here https://docs.docker.com/engine/reference/commandline/events/
        """
