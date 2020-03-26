from ja.server.database.sql.mock_database import MockDatabase
from ja.user.message.add import AddCommand
from ja.user.config.base import UserConfig
from ja.user.config.add import AddCommandConfig
from ja.common.job import JobStatus
from test.server.scheduler.common import get_job
from unittest import TestCase


class AddCommandTest(TestCase):
    """
    Class for testing CancelCommandConfig.
    """

    def setUp(self) -> None:
        self._db = MockDatabase()
        self._job = get_job(user=1, status=JobStatus.NEW).job
        self._job.uid = "1"  # Should be removed
        self._cmd = AddCommand(AddCommandConfig(UserConfig(), self._job))

    def test_admin_can_add_for_other_user(self) -> None:
        self._cmd.effective_user = 0
        response = self._cmd.execute(self._db)
        self.assertTrue(response.is_success)

    def test_add_insufficient_permission(self) -> None:
        self._cmd.effective_user = 2
        response = self._cmd.execute(self._db)
        self.assertFalse(response.is_success)
