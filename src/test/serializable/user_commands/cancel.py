from test.serializable.base import AbstractSerializableTest
from ja.common.proxy.ssh import SSHConfig
from ja.server.database.sql.mock_database import MockDatabase
from ja.user.message.cancel import CancelCommand
from ja.user.config.base import UserConfig, Verbosity
from ja.common.job import JobStatus
from test.server.scheduler.common import get_job


class CancelCommandTest(AbstractSerializableTest):
    """
    Class for testing CancelCommandConfig.
    """

    def setUp(self) -> None:
        self._optional_properties = []

        config = UserConfig(
            ssh_config=SSHConfig(
                hostname="ies", username="pettto", password="1234567890", key_filename="~/.ssh/id_rsa"),
            verbosity=Verbosity.DETAILED)
        self._object = CancelCommand(config=config, label="ies")

        self._object_dict = {
            "label": "ies",
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "ies",
                    "username": "pettto",
                    "password": "1234567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            }
        }

        self._other_object_dict = {
            "label": "is",
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "es",
                    "username": "petto",
                    "password": "124567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            }
        }
        self._db = MockDatabase()

    def test_cancel_insufficient_permissions(self) -> None:
        job = get_job(user=1, status=JobStatus.QUEUED).job
        job.uid = "1"
        self._db.update_job(job)

        cmd = CancelCommand(None, None, job.uid)
        cmd.effective_user = 2
        response = cmd.execute(self._db)

        self.assertFalse(response.is_success)
        self.assertEquals(self._db.find_job_by_id("1").job.status, JobStatus.QUEUED)
