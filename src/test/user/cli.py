import sys
sys.path.insert(0, "C:/Users/malik/Desktop/JobAdder/src")
from unittest import TestCase
from typing import List, cast

from ja.common.job import Job, JobPriority, JobSchedulingConstraints, JobStatus
from ja.common.docker_context import DockerConstraints, DockerContext, MountPoint
from ja.user.message.add import AddCommand
from ja.user.message.query import QueryCommand
from ja.user.message.cancel import CancelCommand
from test.proxy.server_proxy import ServerProxyDummy
from ja.user.cli import UserClientCLIHandler


class CLITest(TestCase):
    """
    Class to test the command line interface.
    """
    commands: List[List[str]] = ["add -s user/program.py -l lab --mount f l a r -p 2 -t 8 -m 8 --pe --bl --owner 1".split(),
                                 "add -s user/program.py -e a@e.de -p low -t 1 -m 2 --owner 9".split(),
                                 "add -s user/program.py -e a@e.de -p low -t 6 -m 4 --owner 9".split(),
                                 "add -s user/program.py -e a@e.de -p high -t 1 -m 4 --owner 9".split(),
                                 "add -c user/add.yaml".split()]

    def setUp(self) -> None:
        self._jobs: List[Job] = [Job(1, "anon@biz.org", JobSchedulingConstraints(JobPriority.HIGH, True, []),
                                     DockerContext("print(2 + 3)\n", [MountPoint("f", "l"), MountPoint("a", "r")]),
                                     DockerConstraints(8, 8), "lab", status=JobStatus.QUEUED),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, False, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(1, 2), status=JobStatus.RUNNING),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, False, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(6, 4), status=JobStatus.QUEUED),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.HIGH, False, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(1, 4), status=JobStatus.QUEUED),
                                 Job(-1, "anon@biz.org", JobSchedulingConstraints(JobPriority.URGENT, False,
                                     ["lic", "lic1"]), DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(5, 8), status=JobStatus.QUEUED)]

        self._proxy = ServerProxyDummy(ssh_config=None)
        self._cli = UserClientCLIHandler("user/p.yaml")
        for i, job in enumerate(self._jobs):
            job.uid = str(i)
        # Adding jobs.
        for i, command in enumerate(CLITest.commands):
            if command[0] == "add":
                parsed_command: AddCommand = cast(AddCommand, self._cli.get_server_command(command))
                self._proxy.add_job(parsed_command.config)
                if i == 1:
                    parsed_command.config.job.status = JobStatus.RUNNING

    def test_jobs_added(self) -> None:
        self.assertCountEqual(self._proxy.jobs, self._jobs)

    def test_query_threads(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query -t 6 8".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[0]), str(self._jobs[2])]))

    def test_query_owner(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --owner 9".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))

    def test_query_priority(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query -p low".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2])]))

    def test_query_uid(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --uid 1 3".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[3])]))

    def test_query_memory(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --memory 1 4".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))

    def test_query_status(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --status running".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1])]))

    def test_query_memory_empty(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --memory 10 40".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "No jobs satisfy these constraints.")

    def test_query_sresources(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("query --sr lic,lic1".split()))
        response: str = self._proxy.query(command).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[4])]))

    def test_cancel_label(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --label lab".split()))
        self._proxy.cancel_job(command)
        self.assertEqual(self._proxy.jobs[0].status, JobStatus.CANCELLED)

    def test_cancel_uid(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --uid 2".split()))
        self._proxy.cancel_job(command)
        self.assertEqual(self._proxy.jobs[2].status, JobStatus.CANCELLED)
