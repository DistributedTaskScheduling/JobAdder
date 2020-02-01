from abc import ABC, abstractmethod
from ja.server.database.database import ServerDatabase
from ja.server.database.types.work_machine import WorkMachine
from typing import Dict, Any, cast

import yaml


class WebRequest(ABC):
    """
    A base class for the different statistics requests.
    """

    @abstractmethod
    def generate_report(self, database: ServerDatabase) -> str:
        """!
        Generate the requested statistics from the data in the database.

        @param database The database to fetch data from.
        @return The requested statistics as a string in YAML format.
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

    def __init__(self, uid: str):
        """!
        Initialize the request response.

        @param uid The uid of the job the report is for.
        """

    def generate_report(self, database: ServerDatabase) -> str:
        pass


class UserJobsRequest(WebRequest):
    """
    Generates the response to the request to list user's jobs.
    """

    def __init__(self, user: str):
        """!
        Initialize the request response.

        @param user The user to report jobs for.
        """

    def generate_report(self, database: ServerDatabase) -> str:
        pass


class PastJobsRequest(WebRequest):
    """
    Generates the response to the request to list jobs which have been running in the past X hours.
    """

    def __init__(self, since: int):
        """!
        Initialize the request response.

        @param since The reported jobs should have been running since this amount of hours ago.
        """

    def generate_report(self, database: ServerDatabase) -> str:
        pass


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
