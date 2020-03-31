from typing import List
from pathlib import Path

from ja.user.proxy import UserServerProxy
from ja.user.cli import UserClientCLIHandler
from ja.user.message.add import AddCommand
from ja.user.message.cancel import CancelCommand
from ja.user.message.query import QueryCommand


class JobAdder:
    """
    The main class for the JobAdder user client.
    """
    def __init__(self, config_path: str = "%s/.config/jobadder" % Path.home(),
                 remote_module: str = "/tmp/jobadder-server.socket", command_string: str = "ja-remote %s") -> None:
        self._cli_handler = UserClientCLIHandler(config_path=config_path)
        self._remote_module = remote_module
        self._command_string = command_string

    def run(self, cli_args: List[str] = None, suppress_help: bool = False) -> None:
        if cli_args is None:
            command = self._cli_handler.get_command_from_cli()
        else:
            command = self._cli_handler.get_server_command(cli_args, suppress_help=suppress_help)
        if command is not None:
            server_proxy = UserServerProxy(
                ssh_config=command.config.ssh_config, remote_module=self._remote_module,
                command_string=self._command_string)
            if isinstance(command, AddCommand):
                print(server_proxy.add_job(command).result_string)
            elif isinstance(command, CancelCommand):
                print(server_proxy.cancel_job(command).result_string)
            elif isinstance(command, QueryCommand):
                print(server_proxy.query(command).result_string)
            else:
                raise NotImplementedError("Command type not supported by proxy: %s" % type(command))
