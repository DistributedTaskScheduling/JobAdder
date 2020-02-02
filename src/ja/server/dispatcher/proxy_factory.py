from abc import ABC, abstractmethod
from typing import Dict

from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from ja.server.proxy.proxy import IWorkerProxy


class WorkerProxyFactoryBase(ABC):
    """
    An abstract base class for a factory for creating and managing WorkerProxies.
    """

    def __init__(self, database: ServerDatabase):
        """!
        Create a new WorkerProxyFactory.

        @param database The database to update when a connection terminates.
        """
        self._database = database
        self._proxy_dict: Dict[str, IWorkerProxy] = dict()

    @abstractmethod
    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        pass

    def get_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        """!
        Get a valid proxy for the given @work_machine.
        @work_machine must be online, otherwise a runtime exception is thrown.

        @param work_machine The work machine to get a proxy for.
        """
        proxy = self._proxy_dict.get(work_machine.uid, None)
        if proxy is None:
            proxy = self._create_proxy(work_machine)
            self._proxy_dict[work_machine.uid] = proxy
        return proxy


class WorkerProxyFactory(WorkerProxyFactoryBase):
    """
    A concrete factory for creating and managing work proxies over the network.
    Whenever a connection terminates, the database will be updated.
    """

    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        pass
