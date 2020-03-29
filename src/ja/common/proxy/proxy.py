from abc import ABC, abstractmethod
from ja.common.proxy.ssh import SSHConfig, ISSHConnection, SSHConnection


class Proxy(ABC):
    """
    Abstract base class that gives remote access to another object (proxy
    design pattern). Communication is done via Message objects. Proxy first
    sends a Command object to Remote. Proxy then receives a Response object
    from Remote to determine the result of the Command message.
    """
    @abstractmethod
    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnection(ssh_config=ssh_config, remote_module=None)


class SingleMessageProxy(Proxy, ABC):
    """
    Abstract base class for proxies that create a new SSHConnection object for
    each Message sent. SSHConnection objects are automatically closed after the
    Message object is sent.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko.
        """
        self._ssh_config = ssh_config


class ContinuousProxy(Proxy, ABC):
    """
    Abstract base class for proxies that immediately establish an
    SSHConnection. Multiple Message objects can be sent via the SSHConnection.
    The SSHConnection remains open until manually closed.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko.
        """
        self._ssh_connection = self._get_ssh_connection(ssh_config=ssh_config)

    def close_ssh_connection(self) -> None:
        self._ssh_connection.close()
