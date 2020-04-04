from unittest import TestCase
from typing import List, cast

from ja.common.job import Job, JobPriority, JobSchedulingConstraints, JobStatus
from ja.common.docker_context import DockerConstraints, DockerContext, MountPoint
from ja.server.database.sql.mock_database import MockDatabase
from ja.user.message.add import AddCommand
from ja.user.message.query import QueryCommand
from ja.user.message.cancel import CancelCommand
from test.proxy.server_proxy import ServerProxyDummy
from ja.user.cli import UserClientCLIHandler


class CLITest(TestCase):
    """
    Class to test the command line interface.
    """
    commands: List[List[str]] = ["add -s test/user/program.py -l lab --mount f l --mount a r -p 2 -t 8 -m 8 --np\
                                 --owner 1".split(),
                                 "add -s test/user/program.py -l lab -e a@e.de -p low -t 1 -m 2 --owner 9".split(),
                                 "add -s test/user/program.py -e a@e.de -p low -t 6 -m 4 --owner 9".split(),
                                 "add -s test/user/program.py -e a@e.de -p high -t 1 -m 4 --owner 9".split(),
                                 "add -c test/user/add.yaml --owner 0".split()]

    def setUp(self) -> None:
        self._db = MockDatabase(max_special_resources={"lic": 1, "lic1": 1})
        self._jobs: List[Job] = [Job(1, "anon@biz.org", JobSchedulingConstraints(JobPriority.HIGH, False, []),
                                     DockerContext("print(2 + 3)\n", [MountPoint("f", "l"), MountPoint("a", "r")]),
                                     DockerConstraints(8, 8), "lab", status=JobStatus.QUEUED),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, True, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(1, 2), "lab", status=JobStatus.RUNNING),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.LOW, True, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(6, 4), status=JobStatus.QUEUED),
                                 Job(9, "a@e.de", JobSchedulingConstraints(JobPriority.HIGH, True, []),
                                     DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(1, 4), status=JobStatus.QUEUED),
                                 Job(0, "anon@biz.org", JobSchedulingConstraints(JobPriority.URGENT, True,
                                     ["lic", "lic1"]), DockerContext("print(2 + 3)\n", []),
                                     DockerConstraints(5, 8), status=JobStatus.QUEUED)]

        self._proxy = ServerProxyDummy(ssh_config=None)
        self._cli = UserClientCLIHandler("test/user/p.yaml")
        for i, job in enumerate(self._jobs):
            job.uid = str(i)
        # Adding jobs.
        for i, command in enumerate(CLITest.commands):
            parsed_command: AddCommand = cast(AddCommand, self._cli.get_server_command(command))
            self._proxy.add_job(parsed_command)
            parsed_command_db: AddCommand = cast(AddCommand, self._cli.get_server_command(command))
            parsed_command_db.config.job.uid = str(i)
            parsed_command_db.execute(self._db)
            if i == 1:
                parsed_command.config.job.status = JobStatus.RUNNING
                parsed_command_db.config.job.status = JobStatus.RUNNING
                self._db.update_job(parsed_command.config.job)

    def test_jobs_added(self) -> None:
        self.assertCountEqual(self._proxy.jobs, self._jobs)
        self.assertCountEqual([entry.job for entry in self._db.query_jobs(None, -1, None)], self._jobs)

    def test_query_threads(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query -t 6 8".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[0]), str(self._jobs[2])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[0]), str(self._jobs[2])]))

    def test_query_owner(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --owner 9".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))

    def test_query_label(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --label lab".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[0]), str(self._jobs[1])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[0]), str(self._jobs[1])]))

    def test_query_priority(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query -p low".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[1]), str(self._jobs[2])]))

    def test_query_uid(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --uid 1 3".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[3])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[1]), str(self._jobs[3])]))

    def test_query_memory(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --memory 1 4".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[1]), str(self._jobs[2]), str(self._jobs[3])]))

    def test_query_status(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --status running".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[1])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[1])]))

    def test_query_memory_empty(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --memory 10 40".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "No jobs satisfy these constraints.")
        self.assertEqual(response1, "No jobs satisfy these constraints.")

    def test_query_sresources(self) -> None:
        command: QueryCommand = cast(QueryCommand, self._cli.get_server_command("-v 2 query --sr lic,lic1".split()))
        response: str = self._proxy.query(command).result_string
        response1: str = command.execute(self._db).result_string
        self.assertEqual(response, "\n".join([str(self._jobs[4])]))
        self.assertEqual(response1, "\n".join([str(self._jobs[4])]))

    def test_cancel_label(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --label lab".split()))
        self._proxy.cancel_job(command)
        command.execute(self._db)
        self.assertEqual(self._db.find_job_by_id("0").job.status, JobStatus.CANCELLED)
        self.assertEqual(self._db.find_job_by_id("1").job.status, JobStatus.CANCELLED)
        self.assertEqual(self._proxy.jobs[0].status, JobStatus.CANCELLED)
        self.assertEqual(self._proxy.jobs[1].status, JobStatus.CANCELLED)
        command1: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --label lab".split()))
        self.assertFalse(command1.execute(self._db).is_success)
        self.assertFalse(self._proxy.cancel_job(command1).is_success)

    def test_cancel_uid(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --uid 2".split()))
        self._proxy.cancel_job(command)
        command.execute(self._db)
        self.assertEqual(self._proxy.jobs[2].status, JobStatus.CANCELLED)
        self.assertEqual(self._db.find_job_by_id("2").job.status, JobStatus.CANCELLED)

    def test_cancel_uid_failure(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --uid 222".split()))
        self.assertFalse(self._proxy.cancel_job(command).is_success)
        self.assertFalse(command.execute(self._db).is_success)

    def test_cancel_label_failure(self) -> None:
        command: CancelCommand = cast(CancelCommand, self._cli.get_server_command("cancel --label no-label".split()))
        self.assertFalse(self._proxy.cancel_job(command).is_success)
        self.assertFalse(command.execute(self._db).is_success)
