from ja.common.proxy.ssh import SSHConfig
from test.serializable.base import AbstractSerializableTest


class SSHConfigTest(AbstractSerializableTest):
    """
    Class for testing SSHConfig.
    """
    def setUp(self) -> None:
        self._optional_properties = ["username", "password", "key_path", "passphrase"]
        self._object = SSHConfig(
            hostname="www.com", username="tux", password="12345", key_path="~/my_key.rsa", passphrase="asdfghjk")
        self._object_dict = {
            "hostname": "www.com", "username": "tux", "password": "12345", "key_path": "~/my_key.rsa",
            "passphrase": "asdfghjk"
        }
        self._other_object_dict = {
            "hostname": "www.com", "username": "linus", "password": "qwerty", "key_path": "~/my_key.rsa",
            "passphrase": "asdfghjk"
        }
