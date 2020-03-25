from ja.common.message.base import Response
from ja.common.message.server import ServerCommand
from ja.server.database.database import ServerDatabase
from ja.server.proxy.command_handler import ServerCommandHandler
from ja.worker.message.base import WorkerServerCommand
from ja.user.message.base import UserServerCommand

import grp
import pwd
from typing import Dict, List, Type, cast
from unittest import TestCase
from unittest.mock import MagicMock


class MockCommand(WorkerServerCommand):
    def __init__(self, user: str) -> None:
        self._user = user

    def to_dict(self) -> Dict[str, object]:
        return {}

    def execute(self, db: ServerDatabase) -> Response:
        pass

    @property
    def username(self) -> str:
        return self._user

    @classmethod
    def from_dict(cls, dct: Dict[str, object]) -> "MockCommand":
        return MockCommand(cast(str, dct["user"]))


class UserMockCommand(UserServerCommand):
    def to_dict(self) -> Dict[str, object]:
        return {}

    def execute(self, db: ServerDatabase) -> Response:
        pass

    @classmethod
    def from_dict(cls, dct: Dict[str, object]) -> "UserMockCommand":
        return UserMockCommand()


class ServerCommandHandlerNoExecute(ServerCommandHandler):

    # Override user/worker commands.
    # Otherwise, to test a user command we need to create a full SSH Config, Command config, etc.
    _user_commands = {
        "UserCommand": UserMockCommand
    }

    _worker_commands = {
        "WorkerCommand": cast(Type[WorkerServerCommand], MockCommand),
    }

    def __init__(self, test: TestCase, admin_group: str):
        self._test = test
        self._admin_group = admin_group
        self._execute_count = 0
        self._running = True
        self._user = -1
        self.response: Dict[str, object] = {}

    def _execute_command(self, command: ServerCommand) -> Dict[str, object]:
        if self._user >= 0:
            self._test.assertEquals(self._user, cast(UserServerCommand, command).effective_user)

        self._test.assertIsNotNone(command)
        self._execute_count += 1
        return self.response

    def assert_called(self, times: int) -> None:
        self._test.assertEquals(self._execute_count, times)

    def set_expect_user(self, user: int) -> None:
        self._user = user


class MockGroup:
    def __init__(self, name: str, members: List[str]):
        self.gr_mem = members
        self.gr_name = name


class MockPwd:
    def __init__(self, uid: int):
        self._uid = uid

    @property
    def pw_uid(self) -> int:
        return self._uid


def mock_pwnam(user: str) -> MockPwd:
    if user == "root":
        return MockPwd(0)
    if user == "user1":
        return MockPwd(1)
    if user == "user2":
        return MockPwd(2)
    return None


class ServerCommandHandlerTest(TestCase):
    def setUp(self) -> None:
        grp.getgrall = MagicMock(return_value=[MockGroup("root", ["user1"]), MockGroup("users", ["user2"])])
        pwd.getpwnam = MagicMock(side_effect=mock_pwnam)
        self._handler = ServerCommandHandlerNoExecute(self, "root")

    def test_admin_checks(self) -> None:
        self.assertTrue(self._handler._user_is_admin("root"))
        self.assertTrue(self._handler._user_is_admin("user1"))
        self.assertFalse(self._handler._user_is_admin("user2"))
        self.assertFalse(self._handler._user_is_admin("unknown_user"))

    def test_user_message(self) -> None:
        self._handler.response = {"status": "ACK"}
        self._handler.set_expect_user(2)
        response = self._handler._check_exit_or_process_command({}, "UserCommand", "user2")
        self._handler.assert_called(1)
        self.assertDictEqual(response, self._handler.response)

    def test_user_message_admin(self) -> None:
        self._handler.response = {"status": "ACK"}
        self._handler.set_expect_user(0)
        response = self._handler._check_exit_or_process_command({}, "UserCommand", "root")
        self._handler.assert_called(1)
        self.assertDictEqual(response, self._handler.response)

    def test_worker_message(self) -> None:
        self._handler.response = {"status": "ACK"}
        response = self._handler._check_exit_or_process_command({"user": "root"}, "WorkerCommand", "user1")
        self._handler.assert_called(1)
        self.assertDictEqual(response, self._handler.response)

    def test_worker_message_no_permission(self) -> None:
        response = self._handler._check_exit_or_process_command({"user": "user1"}, "WorkerCommand", "user2")
        parsed_response = Response.from_dict(response)
        self._handler.assert_called(0)
        self.assertFalse(parsed_response.is_success, False)
        self.assertEquals(parsed_response.result_string,
                          self._handler._INSUFFICIENT_PERM_TEMPLATE % ("user2", "WorkerCommand"))

    def test_invalid_message(self) -> None:
        response = self._handler._check_exit_or_process_command({"user": "user2"}, "Bad", "user2")
        parsed_response = Response.from_dict(response)
        self._handler.assert_called(0)
        self.assertFalse(parsed_response.is_success, False)
        self.assertEquals(parsed_response.result_string, self._handler._UNKNOWN_COMMAND_TEMPLATE % "Bad")

    def test_kill_ok(self) -> None:
        response = self._handler._check_exit_or_process_command({"user": "root"}, "KillCommand", "root")
        self.assertTrue(Response.from_dict(response).is_success)
        self.assertFalse(self._handler._running)

    def test_kill_fails_nonadmin(self) -> None:
        response = self._handler._check_exit_or_process_command({"user": "user2"}, "KillCommand", "user2")
        self.assertFalse(Response.from_dict(response).is_success)
        self.assertTrue(self._handler._running)
