from abc import ABC
from ja.common.message.server import ServerCommand


class WorkerServerCommand(ServerCommand, ABC):
    """
    Base class for server commands sent by worker clients.
    """
