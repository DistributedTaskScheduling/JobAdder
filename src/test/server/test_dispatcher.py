from copy import deepcopy
from unittest import TestCase

from ja.common.job import Job, JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from ja.server.dispatcher.dispatcher import Dispatcher
from test.proxy.worker_proxy_factory import WorkerProxyDummyFactory


class TestDispatcher(TestCase):

    def _assert_distribution_correct_a(self) -> None:
        # Test if jobs are dispatched correctly by invoking the proxies:
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).pause_job(self._uid_1).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_1).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).pause_job(self._uid_2).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_2).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_3).is_success)

        self.assertFalse(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_1).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_2).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_beta).pause_job(self._uid_3).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_3).is_success)

        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_1).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_2).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_3).is_success)

    def _assert_distribution_correct_ab(self) -> None:
        # Test if jobs are dispatched correctly by invoking the proxies:
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).pause_job(self._uid_1).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_1).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).resume_job(self._uid_2).is_success)
        self.assertTrue(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_2).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_alpha).cancel_job(self._uid_3).is_success)

        self.assertFalse(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_1).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_2).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_beta).cancel_job(self._uid_3).is_success)

        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_1).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_2).is_success)
        self.assertFalse(self._factory.get_proxy(self._work_machine_gamma).cancel_job(self._uid_3).is_success)

    def setUp(self) -> None:
        self._factory = WorkerProxyDummyFactory(database=None)
        self._dispatcher = Dispatcher(self._factory)
        self._work_machine_alpha = WorkMachine(uid="worker-alpha")
        self._work_machine_beta = WorkMachine(uid="worker-beta")
        self._work_machine_gamma = WorkMachine(uid="worker-gamma")
        self._generic_job_dict = {
            "status": JobStatus.RUNNING,
            "owner_id": 1008,
            "email": "user@website.com",
            "scheduling_constraints": {"priority": 1, "is_preemptible": True, "special_resources": ["THING"]},
            "docker_context": {
                "dockerfile_source": "ssh localhost",
                "mount_points": [{"source_path": "/home/user", "mount_path": "/home/user"}]
            },
            "docker_constraints": {"cpu_threads": 4, "memory": 4096},
            "label": "thing"
        }
        self._uid_1 = "job001"
        self._uid_2 = "job002"
        self._uid_3 = "job003"

        self._job_1_a = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_1_a.uid = self._uid_1
        self._job_2_a = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_2_a.uid = self._uid_2
        self._job_3_a = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_3_a.uid = self._uid_3
        self._distribution_a = [
            DatabaseJobEntry(job=self._job_1_a, stats=None, machine=self._work_machine_alpha),
            DatabaseJobEntry(job=self._job_2_a, stats=None, machine=self._work_machine_alpha),
            DatabaseJobEntry(job=self._job_3_a, stats=None, machine=self._work_machine_beta),
        ]

        self._job_1_b = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_1_b.uid = self._uid_1
        self._job_2_b = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_2_b.uid = self._uid_2
        self._job_2_b.status = JobStatus.PAUSED
        self._job_3_b = Job.from_dict(deepcopy(self._generic_job_dict))
        self._job_3_b.uid = self._uid_3
        self._job_3_b.status = JobStatus.CANCELLED
        self._distribution_b = [
            DatabaseJobEntry(job=self._job_1_b, stats=None, machine=self._work_machine_alpha),
            DatabaseJobEntry(job=self._job_2_b, stats=None, machine=self._work_machine_alpha),
            DatabaseJobEntry(job=self._job_3_b, stats=None, machine=self._work_machine_beta),
        ]

    def test_dispatch_a(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._assert_distribution_correct_a()

    def test_dispatch_a_idempotent(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_a)
        self._assert_distribution_correct_a()

    def test_dispatch_ab(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_b)
        self._assert_distribution_correct_ab()

    def test_dispatch_ab_idempotent_1(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_b)
        self._assert_distribution_correct_ab()

    def test_dispatch_ab_idempotent_2(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_b)
        self._dispatcher.set_distribution(self._distribution_b)
        self._assert_distribution_correct_ab()

    def test_dispatch_ab_idempotent_3(self) -> None:
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_a)
        self._dispatcher.set_distribution(self._distribution_b)
        self._dispatcher.set_distribution(self._distribution_b)
        self._assert_distribution_correct_ab()
