from ja.common.proxy.ssh import SSHConfig
from test.serializable.base import AbstractSerializableTest

from ja.user.config.base import UserConfig, Verbosity


class UserConfigTest(AbstractSerializableTest):
    """
    Class for testing CancelCommandConfig.
    """

    def setUp(self) -> None:
        self._optional_properties = []
        self._object = UserConfig(ssh_config=SSHConfig(hostname="ies", username="pettto",
                                                       password="1234567890"), verbosity=Verbosity.DETAILED)

        self._object_dict = {
            "verbosity": 2,
            "ssh_config": {
                "hostname": "ies",
                "username": "pettto",
                "password": "1234567890",
                "passphrase": None,
                "key_filename": "~/.ssh/id_rsa"
            }
        }
        self._other_object_dict = {
            "verbosity": 2,
            "ssh_config": {
                "hostname": "is",
                "username": "pttto",
                "password": "134567890",
                "passphrase": None,
                "key_filename": "~/.ssh/id_rsa"
            }
        }
