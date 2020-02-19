from unittest import TestCase
from typing import List

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
    commands: List[List[str]] = ["add -s path -l lab --mount f l a r -p high -t 8 -m 8 --pe --bl --owner 13".split(),
                                 "add -s usr/cool-path -e a@e.de -p low -t 1 -m 2 --owner 9".split(),
                                 "add -s usr/another-path -e a@e.de -p low -t 6 -m 4 --owner 9".split(),
                                 "add -s usr/yet-another-path -e a@e.de -p high -t 1 -m 4 --owner 9".split()]
    jobs: List[Job] = [Job(13, "anon@biz.org", JobSchedulingConstraints(JobPriority.HIGH, True, []),
                           DockerContext("path", [MountPoint("f", "l"), MountPoint("a", "r")]),
                           DockerConstraints(8, 8), "lab", status=JobStatus.QUEUED),
                       Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, False, []),
                           DockerContext("usr/cool-path", []), DockerConstraints(1, 2), status=JobStatus.QUEUED),
                       Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, False, []),
                           DockerContext("usr/another-path", []), DockerConstraints(6, 4), status=JobStatus.QUEUED),
                       Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.HIGH, False, []),
                           DockerContext("usr/yet-another-path", []), DockerConstraints(1, 4), status=JobStatus.QUEUED)]

    def setUp(self) -> None:
        self._proxy = ServerProxyDummy([])
        self._cli = UserClientCLIHandler("p.yaml")
        for i, job in enumerate(CLITest.jobs):
            job.uid = str(i)
        # Adding jobs.
        for command in CLITest.commands:
            if command[0] == "add":
                parsed_command: AddCommand = self._cli.get_server_command(command)
                self._proxy.add_job(parsed_command)

    def test_jobs_added(self) -> None:
        self.assertCountEqual(self._proxy.jobs, CLITest.jobs)

    def test_query(self) -> None:
        command = self._cli.get_server_command("query -t 6 8".split())
        response: List[Job] = self._proxy.query(command)
        self.assertCountEqual(response, [CLITest.jobs[0], CLITest.jobs[2]])

    def test_query1(self) -> None:
        command = self._cli.get_server_command("query -o 9".split())
        response: List[Job] = self._proxy.query(command)
        self.assertCountEqual(response, [CLITest.jobs[1], CLITest.jobs[2], CLITest.jobs[3]])

    def test_query2(self) -> None:
        command = self._cli.get_server_command("query -p low".split())
        response: List[Job] = self._proxy.query(command)
        self.assertCountEqual(response, [CLITest.jobs[1], CLITest.jobs[2]])

    def test_cancel_label(self) -> None:
        command = self._cli.get_server_command("cancel label lab".split())
        self._proxy.cancel_job(command)
        self.assertEqual(self._proxy.jobs[0].status, JobStatus.CANCELLED)

    def test_cancel_uid(self) -> None:
        command = self._cli.get_server_command("cancel uid 2".split())
        self._proxy.cancel_job(command)
        self.assertEqual(self._proxy.jobs[2].status, JobStatus.CANCELLED)
