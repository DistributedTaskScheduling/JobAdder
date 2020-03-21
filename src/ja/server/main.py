from ja.common.job import JobStatus
from ja.server.config import ServerConfig
from ja.server.database.sql.database import SQLDatabase
from ja.server.database.types.work_machine import WorkMachineState
from ja.server.dispatcher.dispatcher import Dispatcher
from ja.server.dispatcher.proxy_factory import WorkerProxyFactory
from ja.server.email_notifier import EmailNotifier, BasicEmailServer
from ja.server.scheduler.algorithm import SchedulingAlgorithm
from ja.server.scheduler.default_algorithm import DefaultSchedulingAlgorithm
from ja.server.scheduler.scheduler import Scheduler
from ja.server.proxy.command_handler import ServerCommandHandler
from ja.server.web.api_server import StatisticsWebServer

import ja.server.scheduler.default_policies as dp


class JobCenter:
    """
    Main class for the central server daemon. Contains singleton objects of the
    following classes: ServerCommandHandler, Database, Scheduler, Dispatcher,
    Notifier, HttpServer.
    """

    @staticmethod
    def _init_algorithm() -> SchedulingAlgorithm:
        cost_function = dp.DefaultCostFunction()
        return DefaultSchedulingAlgorithm(cost_function,
                                          dp.DefaultNonPreemptiveDistributionPolicy(cost_function),
                                          dp.DefaultBlockingDistributionPolicy(),
                                          dp.DefaultPreemptiveDistributionPolicy(cost_function))

    @staticmethod
    def _read_config() -> ServerConfig:
        with open('/etc/jobadder/server.conf') as f:
            return ServerConfig.from_string(f.read())

    def _cleanup(self) -> None:
        for job in self._database.get_current_schedule():
            if job.job.status in [JobStatus.RUNNING, JobStatus.PAUSED]:
                job.job.status = JobStatus.CRASHED
                self._database.update_job(job.job)

        for machine in self._database.get_work_machines():
            machine.resources.deallocate(machine.resources.total_resources - machine.resources.free_resources)
            machine.state = WorkMachineState.OFFLINE
            self._database.update_work_machine(machine)

    def __init__(self) -> None:
        """!
        Initialize the JobAdder server daemon.
        This includes:
        1. Parsing the command line arguments and the configuration file.
        2. Connecting to the configured database.
        3. Initializing the scheduler and the dispatcher.
        4. Starting the web server and the email notifier.
        """

        config = self._read_config()
        self._database = SQLDatabase(host=config.database_config.host,
                                     user=config.database_config.username,
                                     password=config.database_config.password)
        self._cleanup()

        proxy_factory = WorkerProxyFactory(self._database)
        self._dispatcher = Dispatcher(proxy_factory)
        self._scheduler = Scheduler(self._init_algorithm(), self._dispatcher, config.special_resources)

        self._email = EmailNotifier(BasicEmailServer(config.email_config.host,
                                                     config.email_config.port,
                                                     config.email_config.username,
                                                     config.email_config.password))

        if config.web_server_port > 0:
            self._web_server = StatisticsWebServer("", config.web_server_port, self._database)

        self._database.set_scheduler_callback(self._scheduler.reschedule)
        self._database.set_job_status_callback(self._email.handle_job_status_updated)
        self._handler = ServerCommandHandler(self._database, config.admin_group)

    def run(self) -> None:
        """!
        Run the main loop of the server daemon.
        """
        self._handler.main_loop()
        self._cleanup()
