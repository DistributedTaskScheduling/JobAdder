from abc import ABC, abstractmethod
from ja.common.message.base import Serializable
from ja.server.database.database import ServerDatabase
from typing import Dict


class WebRequest(Serializable, ABC):
    """
    A base class for the different statistics requests.
    """

    @abstractmethod
    def generate_report(self, database: ServerDatabase) -> None:
        """!
        Generate the requested statistics from the data in the database.
        """


class WorkMachineWorkloadRequest(WebRequest):
    """
    Generates the response to the machine workload request.
    """

    def __init__(self, uid: str):
        """!
        Initialize the request response.

        @param uid The uid of the work machine this request is for.
        """

    def generate_report(self, database: ServerDatabase) -> None:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass


class JobInformationRequest(WebRequest):
    """
    Generates the response to the job information request.
    """

    def __init__(self, uid: str):
        """!
        Initialize the request response.

        @param uid The uid of the job the report is for.
        """

    def generate_report(self, database: ServerDatabase) -> None:
        pass

    def to_dict(self) -> Dict[str, object]:
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

    def generate_report(self, database: ServerDatabase) -> None:
        pass

    def to_dict(self) -> Dict[str, object]:
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

    def generate_report(self, database: ServerDatabase) -> None:
        pass

    def to_dict(self) -> Dict[str, object]:
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

    def generate_report(self, database: ServerDatabase) -> None:
        pass

    def to_dict(self) -> Dict[str, object]:
        pass
