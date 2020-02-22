from abc import ABC, abstractmethod

from ja.common.proxy.proxy import SingleMessageProxy
from ja.common.message.base import Response
from ja.common.proxy.ssh import SSHConfig
from ja.user.config.add import AddCommandConfig
from ja.user.message.cancel import CancelCommand
from ja.user.message.query import QueryCommand


class IUserServerProxy(SingleMessageProxy, ABC):
    """
    Interface for the proxy for the central server used on the user client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko.
        """

    @abstractmethod
    def add_job(self, add_config: AddCommandConfig) -> Response:
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


class UserServerProxy(IUserServerProxy):
    """
    Implementation for the proxy for the central server used on the user client.
    """

    def add_job(self, add_config: AddCommandConfig) -> Response:
        # Establish connection with server, get the d: ServerDatabase and call execute(d)
        pass

    def cancel_job(self, cancel_command: CancelCommand) -> Response:
        pass

    def query(self, query_command: QueryCommand) -> Response:
        pass
