from ja.user.config.base import UserConfig
from ja.common.job import JobPriority, JobStatus
from datetime import datetime
from typing import List, Tuple


class QueryCommandConfig(UserConfig):
    """
    Config for the query command of the user client. If one of the properties of this class is None it is not
    considered for filtering query results. Only return jobs that satisfy the individual conditions of each property.
    If more than one value is provided for a single property, the condition of the property is satisfied if the job
    matches any of the provided values.
    """

    @property
    def uid(self) -> List[str]:
        """!
        @return: Job uid(s) to filter query results by.
        """

    @property
    def label(self) -> List[str]:
        """!
        @return: Job label(s) to filter query results by.
        """

    @property
    def owner(self) -> List[str]:
        """!
        @return: Job owner name(s) to filter query results by.
        """

    @property
    def priority(self) -> List[JobPriority]:
        """!
        @return: Job priority/priorities to filter query results by.
        """

    @property
    def status(self) -> List[JobStatus]:
        """!
        @return: Job status(es) to filter query results by.
        """

    @property
    def is_preemptible(self) -> bool:
        """!
        @return: Job.is_preemptible value to filter query results by.
        """

    @property
    def special_resources(self) -> List[List[str]]:
        """!
        @return: Special resources to filter query results by.
        """

    @property
    def cpu_threads(self) -> Tuple[int, int]:
        """!
        @return: Lower and upper bound of job CPU thread count to filter query results by.
        """

    @property
    def memory(self) -> Tuple[int, int]:
        """!
        @return: Lower and upper bound of job memory allocation in MB to filter query results by.
        """

    @property
    def before(self) -> datetime:
        """!
        Only return jobs scheduled before this point in time.
        @return: The latest point in time a job of interest was scheduled.
        """

    @property
    def after(self) -> datetime:
        """!
        Only return jobs scheduled after this point in time.
        @return: The earliest point in time a job of interest was scheduled.
        """
