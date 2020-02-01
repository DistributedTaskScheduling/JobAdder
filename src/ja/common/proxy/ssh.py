from typing import Dict
from paramiko import SSHClient, AutoAddPolicy  # type: ignore

from ja.common.message.server import ServerCommand, ServerResponse
from ja.common.message.worker import WorkerCommand, WorkerResponse
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
        self._username = ssh_config.username
        self._client = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        self._client.connect(
            hostname=ssh_config.hostname, username=self._username, password=ssh_config.password,
            key_filename=ssh_config.key_path, passphrase=ssh_config.passphrase
        )
        self._remote = remote

    def send_server_command(self, command: ServerCommand) -> ServerResponse:
        """!
        Sends a ServerCommand to the Remote on the host. Automatically attaches the username specified in ssh_config to
        the ServerCommand.
        @param command: The ServerCommand to sent to the Remote.
        @return: The ServerResponse received from the Remote.
        """
        stdin, stdout, stderr = self._client.exec_command(self._remote)
        stdin.write(command)
        response = ServerResponse.from_string(stdout.read())
        stdin.close()
        stdout.close()
        stderr.close()
        return response

    def send_worker_command(self, command: WorkerCommand) -> WorkerResponse:
        """!
        Sends a WorkerCommand to the Remote on the host. Automatically attaches the username specified in ssh_config to
        the WorkerCommand.
        @param command: The WorkerCommand to sent to the Remote.
        @return: The WorkerResponse received from the Remote.
        """
        stdin, stdout, stderr = self._client.exec_command(self._remote)
        stdin.write(command)
        response = WorkerResponse.from_string(stdout.read())
        stdin.close()
        stdout.close()
        stderr.close()
        return response

    def close(self) -> None:
        """!
        Closes the ssh connection to the host.
        @return None.
        """
        self._client.close()


class SSHConfig(Config):
    """
    Specifies all properties used for establishing a paramiko SSHConnection.
    """
    def __init__(self, hostname: str, username: str = None, password: str = None,
                 key_path: str = None, passphrase: str = None):
        """!
        For the SSHConnection some sort of credentials must be provided: either
        a password or a private key (which might need a passphrase to access).
        Keys placed in ~/.ssh are automatically used if possible.
        @param hostname: The name of the host to connect to, mandatory.
        @param username: The name of the user to use for login, optional.
        @param password: The password to use for login, optional.
        @param key_path: The key pair to use for login, optional.
        @param passphrase: The passphrase to use for decrypting private keys,
        optional.
        """
        self._hostname = hostname
        self._username = username
        self._password = password
        self._key_path = key_path
        self._passphrase = passphrase

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SSHConfig):
            return self.hostname == other.hostname \
                and self.username == other.username \
                and self.password == other.password \
                and self.key_path == other.key_path \
                and self.passphrase == other.passphrase
        else:
            return False

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
    def key_path(self) -> str:
        """!
        @return: The key pair to use for login.
        """
        return self._key_path

    @property
    def passphrase(self) -> str:
        """!
        @return: The passphrase to use for decrypting private keys.
        """
        return self._passphrase

    def to_dict(self) -> Dict[str, object]:
        return_dict: Dict[str, object] = dict()
        return_dict["hostname"] = self.hostname
        return_dict["username"] = self.username
        return_dict["password"] = self.password
        return_dict["key_path"] = self.key_path
        return_dict["passphrase"] = self.passphrase
        return return_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "SSHConfig":
        hostname = cls._get_str_from_dict(property_dict=property_dict, key="hostname")
        username = cls._get_str_from_dict(property_dict=property_dict, key="username", mandatory=False)
        password = cls._get_str_from_dict(property_dict=property_dict, key="password", mandatory=False)
        key_path = cls._get_str_from_dict(property_dict=property_dict, key="key_path", mandatory=False)
        passphrase = cls._get_str_from_dict(property_dict=property_dict, key="passphrase", mandatory=False)
        cls._assert_all_properties_used(property_dict)
        return SSHConfig(
            hostname=hostname, username=username, password=password, key_path=key_path, passphrase=passphrase)
