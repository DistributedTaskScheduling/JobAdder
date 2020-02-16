from ja.common.proxy.ssh import SSHConfig
from test.serializable.base import AbstractSerializableTest


class SSHConfigTest(AbstractSerializableTest):
    """
    Class for testing SSHConfig.
    """

    def setUp(self) -> None:
        self._optional_properties = ["password", "passphrase", "key_filename"]
        self._object = SSHConfig(hostname="ies", username="pettto", password="1234567890")
        self._object_dict = {
            "hostname": "ies",
            "username": "pettto",
            "password": "1234567890",
            "passphrase": None,
            "key_filename": "~/.ssh/id_rsa"
        }
        self._other_object_dict = {
            "hostname": "dalfdjsfksdf",
            "username": "adlfjaslkfjdsjaf",
            "password": "12345",
            "passphrase": "123",
            "key_filename": "/id_rsa"
        }
