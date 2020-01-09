from ja.common.proxy.proxy import SingleMessageProxy
from ja.common.message.server import ServerResponse
from ja.common.proxy.ssh import SSHConfig
from ja.user.config.add import AddCommandConfig
from ja.user.config.kill import CancelCommandConfig
from ja.user.config.query import QueryCommandConfig


class UserServerProxy(SingleMessageProxy):
    """
    Proxy for the central server used on the user client.
    """
    def __init__(self, ssh_config: SSHConfig):
        """!
        @param ssh_config: Config for paramiko.
        """

    def add_job(self, add_config: AddCommandConfig) -> ServerResponse:
        """!
        @param add_config: Config specifying parameters for adding a job.
        @return: The Response from the Server.
        """

    def cancel_job(self, cancel_config: CancelCommandConfig) -> ServerResponse:
        """!
        @param cancel_config: Config specifying parameters for cancelling a
        job.
        @return: The Response from the Server.
        """

    def query(self, query_config: QueryCommandConfig) -> ServerResponse:
        """!
        @param query_config: Config specifying parameters for querying a job.
        @return: The Response from the Server.
        """
