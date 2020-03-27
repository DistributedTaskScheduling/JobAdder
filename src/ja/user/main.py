from typing import List

from ja.user.proxy import UserServerProxy
from ja.user.cli import UserClientCLIHandler
from ja.user.message.add import AddCommand
from ja.user.message.cancel import CancelCommand
from ja.user.message.query import QueryCommand


class JobAdder:
    """
    The main class for the JobAdder user client.
    """
    def __init__(self, config_path: str = "~/.config/jobadder", remote_module: str = "ja.server.proxy.remote",
                 command_string: str = "python3 -m %s") -> None:
        self._cli_handler = UserClientCLIHandler(config_path=config_path)
        self._remote_module = remote_module
        self._command_string = command_string

    def run(self, cli_args: List[str] = None) -> None:
        if cli_args is None:
            command = self._cli_handler.get_command_from_cli()
        else:
            command = self._cli_handler.get_server_command(cli_args)
        server_proxy = UserServerProxy(
            ssh_config=command.config.ssh_config, remote_module=self._remote_module,
            command_string=self._command_string)
        if isinstance(command, AddCommand):
            server_proxy.add_job(command)
        elif isinstance(command, CancelCommand):
            server_proxy.cancel_job(command)
        elif isinstance(command, QueryCommand):
            server_proxy.query(command)
        else:
            raise NotImplementedError("Command type not supported by proxy: %s" % type(command))
