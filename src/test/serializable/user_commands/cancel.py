from test.serializable.base import AbstractSerializableTest
from ja.common.proxy.ssh import SSHConfig
from ja.user.message.cancel import CancelCommand
from ja.user.config.base import UserConfig, Verbosity


class CancelCommandTest(AbstractSerializableTest):
    """
    Class for testing CancelCommandConfig.
    """

    def setUp(self) -> None:
        self._optional_properties = []

        config = UserConfig(ssh_config=SSHConfig(hostname="ies", username="pettto",
                                                 password="1234567890"), verbosity=Verbosity.DETAILED)
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
