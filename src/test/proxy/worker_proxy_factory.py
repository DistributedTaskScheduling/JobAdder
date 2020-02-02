from itertools import permutations
from unittest import TestCase
from typing import List, Tuple

from ja.server.database.types.work_machine import WorkMachine
from ja.server.dispatcher.proxy_factory import WorkerProxyFactoryBase
from ja.server.proxy.proxy import IWorkerProxy
from test.proxy.worker_proxy import WorkerProxyDummy


class WorkerProxyDummyFactory(WorkerProxyFactoryBase):
    """
    Factory class for WorkerProxyDummy.
    """
    def _create_proxy(self, work_machine: WorkMachine) -> IWorkerProxy:
        return WorkerProxyDummy(uid=work_machine.uid, jobs=[])


class WorkerProxyDummyFactoryTest(TestCase):
    """
    Class for testing WorkerProxyDummyFactory.
    """
    def test_retrieval(self) -> None:
        for indices in permutations([0, 1, 2] * 2):
            factory = WorkerProxyDummyFactory(database=None)
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
