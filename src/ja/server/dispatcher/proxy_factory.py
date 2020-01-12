from abc import ABC, abstractmethod
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.proxy.proxy import IWorkerProxy, WorkerProxy


class IWorkerProxyFactory(ABC):
    """
    An abstract factory for creating and managing WorkerProxies.
    """

    @abstractmethod
    def get_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        """!
        Get a valid proxy for the given @work_machine.
        @work_machine must be online, otherwise a runtime exception is thrown.

        @param work_machine The work machine to get a proxy for.
        """


class WorkerProxyFactory(IWorkerProxyFactory):
    """
    A concrete factory for creating and managing work proxies over the network.
    Whenever a connection terminates, the database will be updated.
    """

    def __init__(self, database: ServerDatabase):
        """!
        Create a new WorkerProxyFactory.

        @param database The database to update when a connection terminates.
        """

    def get_proxy(self, work_machine: WorkMachine) -> WorkerProxy:
        """!
        Get a valid proxy for the given @work_machine.
        @work_machine must be online, otherwise a runtime exception is thrown.

        The returned proxies are cached. This means that two calls for the same work machine will return the same
        object, except if the connection is not terminated between the two calls.

        @param work_machine The work machine to get a proxy for.
        """
