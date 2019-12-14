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

    @property
    def hostname(self) -> str:
        """!
        @return: The name of the host to connect to.
        """

    @property
    def username(self) -> str:
        """!
        @return: The name of the user to use for login.
        """

    @property
    def password(self) -> str:
        """!
        @return: The password to use for login.
        """

    @property
    def key_filename(self) -> str:
        """!
        @return: The key pair to use for login.
        """

    @property
    def passphrase(self) -> str:
        """!
        @return: The passphrase to use for decrypting private keys.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "SSHConfig":
        pass

    @classmethod
    def from_string(cls, yaml_string: str) -> "SSHConfig":
        pass
