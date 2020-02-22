from itertools import permutations
from unittest import TestCase
from typing import List, Tuple

from ja.common.proxy.ssh import SSHConfig
from ja.server.database.types.work_machine import WorkMachine
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase
from ja.server.proxy.proxy import IWorkerProxy
from test.proxy.worker_proxy import SSHDummyWorkerProxy
from test.proxy.worker_proxy_dummy import WorkerProxyDummy
from test.abstract import skipIfAbstract


class AbstractWorkerProxyFactoryTest(TestCase):
    """
    Class for testing WorkerProxyDummyFactory.
    """
    def _get_factory(self) -> WorkerProxyFactoryBase:
        pass

    @skipIfAbstract
    def test_retrieval(self) -> None:
        for indices in permutations([0, 1, 2] * 2):
            factory = self._get_factory()
            wm_wmproxy_tuples: List[Tuple[WorkMachine, IWorkerProxy]] = [
                (WorkMachine(uid="worker001"), None),
                (WorkMachine(uid="Worker002"), None),
                (WorkMachine(uid="Worker003"), None),
            ]
            for index in indices:
                work_machine, saved_proxy = wm_wmproxy_tuples[index]
                retrieved_proxy = factory.get_proxy(work_machine)
                self.assertIsNotNone(
                    retrieved_proxy,
                    "Retrieved proxy for index %s in permutation %s is None." % (index, indices)
                )
                if saved_proxy is None:
                    wm_wmproxy_tuples[index] = work_machine, retrieved_proxy
                else:
                    self.assertIs(
                        saved_proxy, retrieved_proxy,
                        "Retrieved a different proxy for index %s in permutation %s" % (index, indices)
                    )


class WorkerProxyDummyFactory(WorkerProxyFactoryBase):
    """
    Factory class for WorkerProxyDummy.
    """
    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        return WorkerProxyDummy(uid=work_machine.uid, jobs=[])


class WorkerProxyDummyFactoryTest(AbstractWorkerProxyFactoryTest):
    """
    Class for testing WorkerProxyDummyFactory.
    """
    def _get_factory(self) -> WorkerProxyFactoryBase:
        return WorkerProxyDummyFactory(database=None)


class SSHDummyWorkerProxyFactory(WorkerProxyFactoryBase):
    """
    Factory class for test implementation of WorkerProxy.
    """
    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        return SSHDummyWorkerProxy(uid=work_machine.uid, ssh_config=SSHConfig(hostname=work_machine.uid))


class WorkerProxyFactoryTest(AbstractWorkerProxyFactoryTest):
    """
    Class for testing WorkerProxyFactory.
    """
    def _get_factory(self) -> WorkerProxyFactoryBase:
        return SSHDummyWorkerProxyFactory(database=None)
