from typing import Dict

from ja.common.message.base import Command, Response
from ja.common.config import Config


class SSHConnection:
    """
    Establishes an SSH connection to a Remote object. Writes Command objects to
    the stdin of said Remote objects. Then reads a Response object from stdout
    of the Remote objects. Message objects are read/written as YAML strings.
    Uses paramiko as the backend for establishing an ssh connection.
    """

    def __init__(self, ssh_config: "SSHConfig", remote: str):
        """!
        Creates a new SSHConnection object. Arguments for establishing the
        actual ssh connection are packaged in @ssh_config. If no credentials
        are provided and no suitable keys were found automatically the
        constructor prompts the user for input.
        @param ssh_config: Config for paramiko.
        @param remote: The name of the Remote to execute on the host.
        """

    def send(self, command: Command) -> Response:
        """!
        Sends a Command to the Remote on the host. Automatically attaches
        the username specified in ssh_config to the Command.
        @param command: The Command to sent to the Remote.
        @return: The Response received from the Remote.
        """

    def close(self) -> None:
        """!
        Closes the ssh connection to the host.
        @return None.
        """


class SSHConfig(Config):
    """
    Specifies all properties used for establishing a paramiko SSHConnection.
    """

    def __init__(self, hostname: str, username: str, password: str = None,
                 key_filename: str = None, passphrase: str = None):
        """!
        For the SSHConnection some sort of credentials must be provided: either
        a password or a private key (which might need a passphrase to access).
        Keys placed in ~/.ssh are automatically used if possible.
        @param hostname: The name of the host to connect to, mandatory.
        @param username: The name of the user to use for login, mandatory.
        @param password: The password to use for login, optional.
        @param key_filename: The key pair to use for login, optional.
        @param passphrase: The passphrase to use for decrypting private keys,
        optional.
        """
        self._hostname = hostname
        self._username = username
        self._password = password
        self._key_filename = key_filename
        self._passphrase = passphrase
        if self._key_filename is None:
            self._key_filename = "~/.ssh/id_rsa"

    @property
    def hostname(self) -> str:
        """!
        @return: The name of the host to connect to.
        """
        return self._hostname

    @property
    def username(self) -> str:
        """!
        @return: The name of the user to use for login.
        """
        return self._username

    @property
    def password(self) -> str:
        """!
        @return: The password to use for login.
        """
        return self._password

    @property
    def key_filename(self) -> str:
        """!
        @return: The key pair to use for login.
        """
        return self._key_filename

    @property
    def passphrase(self) -> str:
        """!
        @return: The passphrase to use for decrypting private keys.
        """
        return self._passphrase

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SSHConfig):
            return self._hostname == o._hostname \
                and self._username == o._username \
                and self._key_filename == o._key_filename \
                and self._password == o._password \
                and self._passphrase == o._passphrase
        else:
            return False

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["hostname"] = self._hostname
        _dict["username"] = self._username
        _dict["password"] = self._password
        _dict["key_filename"] = self._key_filename
        _dict["passphrase"] = self._passphrase
        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "SSHConfig":
        _hostname = cls._get_str_from_dict(property_dict=property_dict, key="hostname")
        _username = cls._get_str_from_dict(property_dict=property_dict, key="username")
        _password = cls._get_str_from_dict(property_dict=property_dict, key="password", mandatory=False)
        _key_filename = cls._get_str_from_dict(property_dict=property_dict, key="key_filename", mandatory=False)
        _passphrase = cls._get_str_from_dict(property_dict=property_dict, key="passphrase", mandatory=False)
        cls._assert_all_properties_used(property_dict)
        return SSHConfig(hostname=_hostname, username=_username, password=_password, key_filename=_key_filename,
                         passphrase=_passphrase)
