from ja.user.message.base import UserServerCommand
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
import argparse
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Tuple, Any


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

    def get_command_from_cli(self) -> UserServerCommand:
        """!
        @return UserServerCommand from Command line arguments
        """
        return self.get_server_command(sys.argv[1:])

    @staticmethod
    def _get_option(option: str, arg: Any, default: Any, config: Dict[str, Any]) -> Any:
        if arg is None:
            if option in config:
                return config[option]
            else:
                return default
        return arg

    def get_server_command(self, cli_args: List[str]) -> UserServerCommand:
        """!
        Transforms string arguments into a UserConfig object. Creates and returns a UserServerCommand object from the
        command line arguments combined with the general config loaded in the constructor.
        @return: The UserServerCommand created from the combined input.
        """

        with open(self._config_path, "r") as stream:
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
                            help="The name of the server to connect to.")
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
        parser_add.add_argument("--config", "-c", help="Config file path for adding a job.")
        parser_add.add_argument("--label", "-l", help="Label for the job.")
        parser_add.add_argument("--source", "-s", "--path", help="Path of the source file containing the job.")
        parser_add.add_argument("--priority", "-p", choices="low medium high urgent 0 1 2 3".split())
        parser_add.add_argument("--threads", "-t", type=int, help="Assign a number of cpu threads for your job.")
        parser_add.add_argument("--memory", "-m", type=int, help="Assign a specific amount of memory to your job")
        parser_add.add_argument("--non-preemptible", "--np", action="store_true", help="Non preemptible job.")
        parser_add.add_argument("--blocking", "--bl", action="store_true", help=argparse.SUPPRESS)
        parser_add.add_argument("--mount", nargs=2, action="append")
        parser_add.add_argument("--email", "-e", required=email is None, default=email)
        parser_add.add_argument("--special-resources", "--sr", nargs="+",
                                help="Add the required special resources for a job.")
        parser_add.add_argument("--owner", default=-1, type=int, help=argparse.SUPPRESS)

        # parser for query command
        parser_query = subparsers.add_parser("query")
        parser_query.add_argument("--uid", "-u", nargs="+", help="Job uid(s) to filter query results by.")
        parser_query.add_argument("--label", "-l", nargs="+", help="Job label(s) to filter query results by.")
        parser_query.add_argument("--owner", "-o", nargs="+", help="Job owners to filter query results by.")
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
                                  help="Get job(s) that can be preempted by other jobs.")
        parser_query.add_argument("--special-resources", "--sr", help="Filter by the special resources of a job. \
                                                                       Special resources are separated bx a comma \
                                                                       and lists of speacial resources are separated \
                                                                       by a point. \
                                                                       [sr,sr1,sr2,sr3].[...].[...]...")
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
        parser_cancel = subparsers.add_parser("cancel", help="A job can be cancelled by either specifying \
                                                              its uid or its label, both are not possible.")
        parser_cancel.add_argument("--label", "-l", help="Label of the job that will be cancelled.")
        parser_cancel.add_argument("--uid", "-u", help="Uid of the job that will be cancelled.")

        args: Namespace = parser.parse_args(cli_args)
        ssh_config = SSHConfig(args.hostname, args.username, args.password, args.key_path, args.passphrase)
        user_config = UserConfig(ssh_config, Verbosity(args.verbosity))

        if args.command == "add":
            label: str = args.label
            source: str = args.source
            priority: str = args.priority
            threads: int = args.threads
            memory: int = args.memory
            preemptible: bool = not args.non_preemptible
            blocking: bool = args.blocking
            mount: List[List[str]] = args.mount
            special_resources: List[str] = args.special_resources

            add_file = {}
            if args.config is not None:
                with open(args.config, "r") as stream:
                    add_file = yaml.safe_load(stream)
            label = UserClientCLIHandler._get_option("label", label, None, add_file)
            source = UserClientCLIHandler._get_option("source", source, None, add_file)
            priority = UserClientCLIHandler._get_option("priority", priority, "1", add_file)
            threads = UserClientCLIHandler._get_option("threads", threads, -1, add_file)
            memory = UserClientCLIHandler._get_option("memory", memory, 1, add_file)
            mount = UserClientCLIHandler._get_option("mount", mount, [], add_file)
            special_resources = UserClientCLIHandler._get_option("special-resources",
                                                                 special_resources, [], add_file)
            if "blocking" in add_file:
                blocking = blocking or add_file["blocking"]
            if "preemptible" in add_file:
                preemptible = preemptible or add_file["preemptible"]
            if source is None:
                raise ValueError("No source file was specified in the config file or the CLI, use the -s option.")

            # creating job instance
            with open(source, "r") as file:
                source = file.read()
            constraints: JobSchedulingConstraints = JobSchedulingConstraints(UserClientCLIHandler._pr[priority],
                                                                             preemptible,
                                                                             special_resources)
            docker_constraints: DockerConstraints = DockerConstraints(threads, memory)
            mount_points: List[MountPoint] = []
            for pt in mount:
                mount_points.append(MountPoint(pt[0], pt[1]))
            docker_context: DockerContext = DockerContext(source, mount_points)
            job: Job = Job(args.owner, args.email, constraints, docker_context, docker_constraints, label=label)

            add_config = AddCommandConfig(user_config, job, blocking=blocking)
            add_command: AddCommand = AddCommand(add_config)

            return add_command

        elif args.command == "query":
            uids: List[str] = args.uid
            labels: List[str] = args.label
            owners: List[str] = args.owner
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
            special_resources_query: List[List[str]] = None
            if args.special_resources is not None:
                special_resources_query = [sr.split(",") for sr in args.special_resources.split(".")]
            threads_query: Tuple[int, int] = None if args.threads is None else (args.threads[0], args.threads[1])
            memory_query: Tuple[int, int] = None if args.memory is None else (args.memory[0], args.memory[1])
            # these only work in python 3.7 and newer
            before = None if args.before is None else datetime.fromisoformat(args.before)
            after = None if args.after is None else datetime.fromisoformat(args.after)

            query_command = QueryCommand(user_config, uids, labels, owners,
                                         priorities, statuses, is_preemptible,
                                         special_resources_query, threads_query, memory_query,
                                         before, after)

            return query_command

        elif args.command == "cancel":
            return CancelCommand(user_config, label=args.label, uid=args.uid)
        return None
