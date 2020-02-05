from abc import ABC, abstractmethod
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from typing import Dict, Any, Optional, cast

import datetime
import yaml
import pwd


class WebRequest(ABC):
    """
    A base class for the different statistics requests.
    """
    TIMESTAMP_FORMAT: str = "%Y-%d-%m %H:%M:%S"

    @abstractmethod
    def generate_report(self, database: ServerDatabase) -> Optional[str]:
        """!
        Generate the requested statistics from the data in the database.

        @param database The database to fetch data from.
        @return The requested statistics as a string in YAML format. If the request is invalid (for ex. job does not
          exist), the YAML document consists of only one value `error`, explaining the problem.
        """


class WorkMachineWorkloadRequest(WebRequest):
    """
    Generates the response to the machine workload request.
    """

    @staticmethod
    def _machine_to_dict(machine: WorkMachine) -> Dict[str, Any]:
        free = machine.resources.free_resources
        used = machine.resources.total_resources - machine.resources.free_resources
        return {
            "id": machine.uid,
            "cpu_load": {"used": used.cpu_threads, "free": free.cpu_threads},
            "memory_load": {"used": used.memory, "free": free.memory},
            "swap_space": {"used": used.swap, "free": free.swap},
        }

    def generate_report(self, database: ServerDatabase) -> str:
        report: Dict[str, Any] = {}
        report["machines"] = []

        for m in database.get_work_machines():
            report["machines"] += [self._machine_to_dict(m)]

        return cast(str, yaml.dump(report))


class JobInformationRequest(WebRequest):
    """
    Generates the response to the job information request.
    """
    NO_SUCH_JOB_TEMPLATE: str = "No job with UID %s found in the database."

    def __init__(self, uid: str):
        """!
        Initialize the request response.

        @param uid The uid of the job the report is for.
        """
        self._job_uid = uid

    def generate_report(self, database: ServerDatabase) -> str:
        job = database.find_job_by_id(self._job_uid)
        if not job:
            return cast(str, yaml.dump({"error": self.NO_SUCH_JOB_TEMPLATE % self._job_uid}))

        response_dict = {
            "user_name": pwd.getpwuid(job.job.owner_id).pw_name,
            "user_id": job.job.owner_id,
            "priority": job.job.scheduling_constraints.priority.name,
            "scheduled_at": job.statistics.time_added.strftime(WebRequest.TIMESTAMP_FORMAT),
            "time_spent_running": job.statistics.running_time,
            "allocated_threads": job.job.docker_constraints.cpu_threads,
            "allocated_ram": job.job.docker_constraints.memory,
        }
        return cast(str, yaml.dump(response_dict))


class JobListRequestBase(WebRequest, ABC):
    @staticmethod
    def _query_database(database: ServerDatabase,
                        owner: int = -1,
                        since: datetime.datetime = None,
                        machine: WorkMachine = None) -> str:
        jobs = database.query_jobs(user_id=owner, since=since, work_machine=machine)
        response_dict: Dict[str, Any] = {"jobs": []}
        for job in jobs:
            response_dict["jobs"] += [{"job_id": job.job.uid}]
        return cast(str, yaml.dump(response_dict))


class UserJobsRequest(JobListRequestBase):
    """
    Generates the response to the request to list user's jobs.
    """
    NO_SUCH_USER_TEMPLATE = "Unix user with name '%s' does not exist."

    def __init__(self, user: str):
        """!
        Initialize the request response.

        @param user The user to report jobs for.
        """
        self._user = user

    def generate_report(self, database: ServerDatabase) -> str:
        try:
            uid = pwd.getpwnam(self._user).pw_uid
        except KeyError:
            return cast(str, yaml.dump({"error": self.NO_SUCH_USER_TEMPLATE % self._user}))

        return self._query_database(database, owner=uid)


class PastJobsRequest(JobListRequestBase):
    """
    Generates the response to the request to list jobs which have been running in the past X hours.
    """

    def __init__(self, since: int):
        """!
        Initialize the request response.

        @param since The reported jobs should have been running since this amount of hours ago.
        """
        self._since = datetime.datetime.now() - datetime.timedelta(hours=since)

    def generate_report(self, database: ServerDatabase) -> str:
        return self._query_database(database, since=self._since)


class WorkMachineJobsRequest(WebRequest):
    """
    Generates the response to the request to list jobs which are running on the given work machine.
    """

    def __init__(self, workmachine_id: str):
        """!
        Initialize the request response.

        @param workmachine_id The work machine the request is for.
        """

    def generate_report(self, database: ServerDatabase) -> str:
        pass
