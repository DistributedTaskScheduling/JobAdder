"""
This module contains classes and definitions related to handling
ServerCommands.
"""

from ja.common.message.base import Response
from ja.common.proxy.command_handler import CommandHandler
from ja.server.database.database import ServerDatabase
from typing import Dict, Type, cast

from ja.worker.message.base import WorkerServerCommand
from ja.worker.message.register import RegisterWorkerCommand
from ja.worker.message.done import JobDoneCommand
from ja.worker.message.crashed import JobCrashedCommand
from ja.worker.message.retire import RetireWorkerCommand

from ja.common.message.server import ServerCommand
from ja.user.message.add import AddCommand
from ja.user.message.query import QueryCommand
from ja.user.message.cancel import CancelCommand

import logging

logger = logging.getLogger(__name__)


class ServerCommandHandler(CommandHandler):
    """
    ServerCommandHandler receives ServerMessages and performs the corresponding
    actions on the server.
    """
    def __init__(self, database: ServerDatabase, socket_path: str, admin_group: str):
        """!
        @param database The server database.
        @param socket_path: the path to the unix named socket to listen on.
        @param admin_group: the Unix group to grant administrative privileges to.
        """
        super().__init__(socket_path, admin_group)
        self._database = database

    _user_commands = {
        "AddCommand": AddCommand,
        "QueryCommand": QueryCommand,
        "CancelCommand": CancelCommand,
    }

    # User commands which can be run by everybody
    _unsecured_user_commands = ["QueryCommand"]

    _worker_commands = {
        "RegisterWorkerCommand": RegisterWorkerCommand,
        "JobDoneCommand": JobDoneCommand,
        "JobCrashedCommand": JobCrashedCommand,
        "RetireWorkerCommand": RetireWorkerCommand,
    }

    def _execute_command(self, command: ServerCommand) -> Dict[str, object]:
        logger.info("executing %s command" % type(command).__name__)
        logger.debug(str(command))
        r_dict = command.execute(self._database)
        logger.info("Command executed successfully: %s" % r_dict.is_success)
        logger.debug("Response: %s" % str(r_dict))
        return r_dict.to_dict()

    def _process_exit_message(self, type_name: str, user: str) -> Dict[str, object]:
        if type_name != "KillCommand":
            return None
        if not self._user_is_admin(user):
            return Response("Insufficient permissions to shut down the server.", False).to_dict()
        self._running = False
        return Response("Shutting down server ...", True).to_dict()

    def _process_worker_message(self, command_dict: Dict[str, object], type_name: str, user: str) -> Dict[str, object]:
        if type_name not in self._worker_commands:
            return None

        if not self._user_is_admin(user):
            return Response(self._INSUFFICIENT_PERM_TEMPLATE % (user, type_name), False).to_dict()

        command = cast(Type[WorkerServerCommand], self._worker_commands[type_name]).from_dict(command_dict)
        worker_command: WorkerServerCommand = cast(WorkerServerCommand, command)
        return self._execute_command(worker_command)

    def _process_user_message(self, command_dict: Dict[str, object], type_name: str, user: str) -> Dict[str, object]:
        if type_name not in self._user_commands:
            return None

        command = cast(Type[WorkerServerCommand], self._user_commands[type_name]).from_dict(command_dict)
        server_command: ServerCommand = cast(WorkerServerCommand, command)
        if type_name not in self._unsecured_user_commands:
            if user != server_command.username and not self._user_is_admin(user):
                return Response(self._INSUFFICIENT_PERM_TEMPLATE % (user, type_name), False).to_dict()
        return self._execute_command(server_command)

    def _process_command_dict(
            self, command_dict: Dict[str, object], type_name: str, username: str) -> Dict[str, object]:
        response = self._process_exit_message(type_name, username)
        if response:
            return response

        response = self._process_worker_message(command_dict, type_name, username)
        if response:
            return response

        response = self._process_user_message(command_dict, type_name, username)
        if response:
            return response

        return Response(self._UNKNOWN_COMMAND_TEMPLATE % type_name, False).to_dict()
