from ja.server.database.types.job_entry import JobRuntimeStatistics
from unittest import TestCase
from datetime import datetime
import time


class JobRuntimeStatisticsTest(TestCase):
    """
    Class to test JobRuntimeStatistics
    """

    def test_constructor_start(self) -> None:
        started: datetime = datetime.fromtimestamp(time.time())
        added: datetime = datetime.fromtimestamp(time.time())
        running_time = 800
        with self.assertRaises(ValueError):
            JobRuntimeStatistics(added, started, running_time)

    def test_constructor_running_time(self) -> None:
        added: datetime = datetime.fromtimestamp(time.time())
        started: datetime = datetime.fromtimestamp(time.time())
        running_time = -123
        with self.assertRaises(ValueError):
            JobRuntimeStatistics(added, started, running_time)
