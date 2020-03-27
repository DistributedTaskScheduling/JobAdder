from abc import ABC, abstractmethod

from ja.common.proxy.proxy import SingleMessageProxy
from ja.common.message.base import Response
from ja.common.proxy.ssh import SSHConnection, ISSHConnection, SSHConfig
from ja.user.message.add import AddCommand
from ja.user.message.cancel import CancelCommand
from ja.user.message.query import QueryCommand


class IUserServerProxy(SingleMessageProxy, ABC):
    """
    Interface for the proxy for the central server used on the user client.
    """

    @abstractmethod
    def add_job(self, add_config: AddCommand) -> Response:
        """!
        @param add_config: Config specifying parameters for adding a job.
        @return: The Response from the Server.
        """

    @abstractmethod
    def cancel_job(self, cancel_command: CancelCommand) -> Response:
        """!
        @param cancel_command: Config specifying parameters for cancelling a
        job.
        @return: The Response from the Server.
        """

    @abstractmethod
    def query(self, query_command: QueryCommand) -> Response:
        """!
        @param query_command: Config specifying parameters for querying a job.
        @return: The Response from the Server.
        """


class UserServerProxyBase(IUserServerProxy, ABC):
    """
    Base class for the proxy for the central server used on the user client.
    """

    def add_job(self, add_command: AddCommand) -> Response:
        connection = self._get_ssh_connection(add_command.config.ssh_config)
        return connection.send_command(add_command)

    def cancel_job(self, cancel_command: CancelCommand) -> Response:
        connection = self._get_ssh_connection(cancel_command.config.ssh_config)
        return connection.send_command(cancel_command)

    def query(self, query_command: QueryCommand) -> Response:
        connection = self._get_ssh_connection(query_command.config.ssh_config)
        return connection.send_command(query_command)


class UserServerProxy(UserServerProxyBase):
    """
    Implementation for the proxy for the central server used on the user client.
    """
    def __init__(self, ssh_config: SSHConfig, remote_module: str = "ja.server.proxy.remote",
                 command_string: str = "python3 -m %s"):
        super().__init__(ssh_config=ssh_config)
        self._remote_module = remote_module
        self._command_string = command_string

    def _get_ssh_connection(self, ssh_config: SSHConfig) -> ISSHConnection:
        return SSHConnection(
            ssh_config=ssh_config, remote_module=self._remote_module, command_string=self._command_string)
