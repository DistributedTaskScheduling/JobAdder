from ja.common.job import Job
from ja.server.database.database import ServerDatabase


class EmailNotifier:
    """
    EmailNotifier is responsible for listening for changes in the database and sending emails to the owners of jobs
    when their jobs finish running.
    """
    def __init__(self, database: ServerDatabase):
        """!
        Initialize the email notifier, and set the callback for the given database.

        @param database The database to notify jobs for.
        """

    def _handle_job_status_updated(self, job: Job) -> None:
        """!
        Check whether a notification should be sent for the given job, and if yes, send it.
        A notification is sent only when the job is no longer running.

        @param job The job whose status was updated.
        """
