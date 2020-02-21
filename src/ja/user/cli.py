from ja.common.message.server import ServerCommand
from ja.common.job import Job, JobSchedulingConstraints, JobPriority, JobStatus
from ja.common.docker_context import DockerConstraints, DockerContext, MountPoint
from ja.user.config.add import AddCommandConfig
from ja.user.message.add import AddCommand
from ja.user.message.query import QueryCommand
from ja.user.message.cancel import CancelCommand
from ja.user.config.base import Verbosity, UserConfig
from ja.common.proxy.ssh import SSHConfig

import sys
import yaml
from datetime import datetime
import os
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Tuple


class UserClientCLIHandler:
    """
    Class for handling user input on the user client.
    """

    _pr: Dict[str, JobPriority] = {"0": JobPriority.LOW,
                                   "low": JobPriority.LOW,
                                   "1": JobPriority.MEDIUM,
                                   "medium": JobPriority.MEDIUM,
                                   "2": JobPriority.HIGH,
                                   "high": JobPriority.HIGH,
                                   "3": JobPriority.URGENT,
                                   "urgent": JobPriority.URGENT}

    _statuses: Dict[str, JobStatus] = {"0": JobStatus.NEW,
                                       "new": JobStatus.NEW,
                                       "1": JobStatus.QUEUED,
                                       "queued": JobStatus.QUEUED,
                                       "2": JobStatus.RUNNING,
                                       "running": JobStatus.RUNNING,
                                       "3": JobStatus.PAUSED,
                                       "paused": JobStatus.PAUSED,
                                       "4": JobStatus.DONE,
                                       "done": JobStatus.DONE,
                                       "5": JobStatus.CANCELLED,
                                       "killed": JobStatus.CANCELLED,
                                       "6": JobStatus.CRASHED,
                                       "crashed": JobStatus.CRASHED}

    def __init__(self, config_path: str):
        """!
        Receives a path to a general user client config file.
        @param config_path: The path of the general config file.
        """
        self._config_path = config_path

    def get_command_from_cli(self) -> ServerCommand:
        """!
        @return ServerCommand from Command line arguments
        """
        return self.get_server_command(sys.argv[1:])

    def get_server_command(self, cli_args: List[str]) -> ServerCommand:
        """!
        Transforms string arguments into a UserConfig object. Creates and returns a ServerCommand object from the
        command line arguments combined with the general config loaded in the constructor.
        @return: The ServerCommand created from the combined input.
        """

        with open(self._config_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        # Creating a UserConfig instance from the user config file.
        verbosity: int = 1 if "verbosity" not in data_loaded else data_loaded["verbosity"]
        hostname: str = None if "hostname" not in data_loaded else data_loaded["hostname"]
        username: str = None if "username" not in data_loaded else data_loaded["username"]
        password: str = None if "password" not in data_loaded else data_loaded["password"]
        key_path: str = None if "key_path" not in data_loaded else data_loaded["key_path"]
        passphrase: str = None if "passphrase" not in data_loaded else data_loaded["passphrase"]
        email: str = None if "email" not in data_loaded else data_loaded["email"]

        parser: ArgumentParser = ArgumentParser("JobAdder: add, cancel or a query a job.")
        # shared options
        parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=verbosity)
        parser.add_argument("--hostname", "--host", type=str,
                            required=hostname is None, default=hostname,
                            help="The name of the host to connect to.")
        parser.add_argument("--username", "--user", type=str,
                            required=username is None, default=username,
                            help="The name of the user to use for login.")
        parser.add_argument("--password", "--pass", type=str, default=password, help="The password to use for login.")
        parser.add_argument("--key-path", "--kp", type=str, default=key_path, help="The key pair to use for login.")
        parser.add_argument("--passphrase", "--pp", type=str, default=passphrase,
                            help="The passphrase to use for decrypting private keys.")

        subparsers = parser.add_subparsers(dest="command")
        # parser for add command.
        parser_add = subparsers.add_parser("add")
        parser_add.add_argument("--label", "-l", help="Label for the job.")
        parser_add.add_argument("--source", "-s", required=True, help="Path of the source file containing the job.")
        parser_add.add_argument("--priority", "-p",
                                choices="low medium high urgent 0 1 2 3".split(),
                                default="1")
        parser_add.add_argument("--threads", "-t", type=int, default=-1,
                                help="Assign a number of cpu threads required for your job.")
        parser_add.add_argument("--memory", "-m",
                                type=int, default=1,
                                help="Assign a specific amount of memory to your job")
        parser_add.add_argument("--preemptible", "--pe", action="store_true")
        parser_add.add_argument("--blocking", "--bl", action="store_true")
        parser_add.add_argument("--mount", nargs="+", type=str, default=[])
        parser_add.add_argument("--email", "-e", required=email is None, default=email)
        parser_add.add_argument("--special-resources", "--sr", nargs="+", default=[])
        parser_add.add_argument("--owner", default=os.getuid(), type=int, help="Not to be used outside of testing!")

        # parser for query command
        parser_query = subparsers.add_parser("query")
        parser_query.add_argument("--uid", "-u", nargs="+", help="Job uid(s) to filter query results by.")
        parser_query.add_argument("--label", "-l", nargs="+", help="Job label(s) to filter query results by.")
        parser_query.add_argument("--owner", "-o", nargs="+", type=int, help="Job owners to filter query results by.")
        parser_query.add_argument("--priority", "-p",
                                  nargs="+",
                                  choices="low medium high urgent 0 1 2 3".split(),
                                  help="Job priorities to filter query results by.")
        parser_query.add_argument("--status",
                                  nargs="+",
                                  choices="new queued running paused done killed crashed 0 1 2 3 4 5 6".split(),
                                  help="Job status(es) to filter query results by.")
        parser_query.add_argument("--preemptible", "--is-preemptible", "--ip",
                                  dest="preemptible",
                                  choices="false true t f".split(),
                                  help="Job.is_preemptible value to filter query results by.")
        parser_query.add_argument("--special-resources", "--sr", nargs="+")
        parser_query.add_argument("--threads", "-t",
                                  nargs=2,
                                  type=int,
                                  help="Lower and upper bound of job CPU thread count to filter query results by.")
        parser_query.add_argument("--memory", "-m",
                                  nargs=2,
                                  type=int,
                                  help="Lower and upper bound of job memory allocation in MB\
                                        to filter query results by.")
        parser_query.add_argument("--before",
                                  help="Jobs scheduled before this point in time (YYYY-MM-DD[ HH:MM:SS]).")
        parser_query.add_argument("--after",
                                  help="Jobs scheduled after this point in time (YYYY-MM-DD[ HH:MM:SS]).")

        # parser for cancel command
        parser_cancel = subparsers.add_parser("cancel")
        parser_cancel.add_argument("label_or_uid",
                                   choices=["label", "uid"],
                                   help="You can cancel a job by specifying its uid OR its label")
        parser_cancel.add_argument("arg", help="The uid or label of the job that needs to be cancelled.")

        args: Namespace = parser.parse_args(cli_args)
        ssh_config = SSHConfig(args.hostname, args.username, args.password, args.key_path, args.passphrase)
        user_config = UserConfig(ssh_config, Verbosity(args.verbosity))

        if args.command == "add":
            # creating job instance
            constraints: JobSchedulingConstraints = JobSchedulingConstraints(UserClientCLIHandler._pr[args.priority],
                                                                             args.preemptible,
                                                                             args.special_resources)
            docker_constraints: DockerConstraints = DockerConstraints(args.threads, args.memory)
            mount_points: List[MountPoint] = []
            for i in range(0, len(args.mount), 2):
                mount_points.append(MountPoint(args.mount[i], args.mount[i + 1]))
            docker_context: DockerContext = DockerContext(args.source, mount_points)
            job: Job = Job(args.owner, args.email, constraints, docker_context, docker_constraints, label=args.label)

            add_config = AddCommandConfig(user_config, job, args.blocking)
            add_command: AddCommand = AddCommand(add_config)

            return add_command

        elif args.command == "query":
            uids: List[str] = args.uid
            labels: List[str] = args.label
            owners: List[int] = args.owner
            priorities: List[JobPriority] = None if args.priority is None else [UserClientCLIHandler._pr[priority]
                                                                                for priority in args.priority]

            statuses: List[JobStatus] = None if args.status is None else [UserClientCLIHandler._statuses[status]
                                                                          for status in args.status]
            if args.preemptible in ["true", "t"]:
                is_preemptible = True
            elif args.preemptible in ["false", "f"]:
                is_preemptible = False
            elif args.preemptible is None:
                is_preemptible = None
            special_resources = args.special_resources
            threads: Tuple[int, int] = None if args.threads is None else (args.threads[0], args.threads[1])
            memory: Tuple[int, int] = None if args.memory is None else (args.memory[0], args.memory[1])
            # these only work in python 3.7 and newer
            before = None if args.before is None else datetime.fromisoformat(args.before)
            after = None if args.after is None else datetime.fromisoformat(args.after)

            query_command = QueryCommand(user_config, uids, labels, owners,
                                         priorities, statuses, is_preemptible,
                                         special_resources, threads, memory,
                                         before, after)

            return query_command

        elif args.command == "cancel":
            cancel_command: CancelCommand = None
            if args.label_or_uid == "label":
                cancel_command = CancelCommand(user_config, label=args.arg, uid=None)
            elif args.label_or_uid == "uid":
                cancel_command = CancelCommand(user_config, label=None, uid=args.arg)
            return cancel_command
        return None
