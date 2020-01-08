from ja.server.database.database import ServerDatabase
from ja.server.scheduler.algorithm import SchedulingAlgorithm


class Scheduler:
    """
    Scheduler is a class which is responsible for generating the new job
    distribution whenever the database changes.

    Internally it uses a SchedulingAlgorithm to determine how to schedule
    jobs which are still runnable.
    """

    def __init__(self, algorithm: SchedulingAlgorithm):
        """!
        Initialize a Scheduler.

        @param algorithm The scheduling algorithm to use to assign jobs to
          work machines.
        """

    def reschedule(self, database: ServerDatabase) -> None:
        """!
        Fetches the current schedule from the database, unassigns work machines
        from jobs which are no longer runnable, and redistributes the other
        jobs using the scheduling algorithm. Finally, the each modified job and
        work machine are updated in the database.

        @param database The database to fetch job schedule from.
        """
