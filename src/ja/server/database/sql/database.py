from datetime import datetime
from typing import List
from ja.common.job import Job
from ja.server.database.types.job_entry import DatabaseJobEntry
from ja.server.database.types.work_machine import WorkMachine
from ja.server.database.database import ServerDatabase


class SQLDatabase(ServerDatabase):
    """!
    SQL Database is the actual implementation of the database used by default
    in JobAdder.
    """

    def __init__(self, host: str, user: str, password: str):
        """!
        Create the SQLDatabase object and connect to the given database.

        @param host The host of the database to connect to.
        @param user The username to use for the connection.
        @param passowrd The password to use for the connection.
        """

    def find_job_by_id(self, job_id: str) -> Job:
        pass

    def update_job(self, job: Job) -> None:
        pass

    def assign_job_machine(self, job: Job, machine: WorkMachine) -> None:
        pass

    def update_work_machine(self, machine: WorkMachine) -> None:
        pass

    def get_work_machines(self) -> List[WorkMachine]:
        pass

    def get_current_schedule(self) -> ServerDatabase.JobDistribution:
        pass

    def query_jobs(self, since: datetime,
                   user_id: int,
                   work_machine: WorkMachine) -> List[DatabaseJobEntry]:
        pass

    def set_scheduler_callback(self, callback:
                               ServerDatabase.RescheduleCallback) -> None:
        pass
