from typing import Dict
from ja.user.message.base import UserServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.user.config.add import AddCommandConfig
from ja.common.job import Job, JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry


class AddCommand(UserServerCommand):
    """
    Command for adding a job.
    """
    def __init__(self, config: AddCommandConfig):
        """!
        @param config: Config to create the add command from.
        """
        self._config = config

    @property
    def config(self) -> AddCommandConfig:
        """!
        @return the AddCommandConfig for this Command.
        """
        return self._config

    def to_dict(self) -> Dict[str, object]:
        return self._config.to_dict()

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "AddCommand":
        return AddCommand(AddCommandConfig.from_dict(property_dict))

    def execute(self, database: ServerDatabase) -> Response:
        job: Job = self.config.job
        if self.effective_user != 0 and self.effective_user != job.owner_id:
            return Response(result_string="Cannot submit jobs for other users.", is_success=False)

        db_job_id: DatabaseJobEntry = database.find_job_by_id(job.uid)
        if db_job_id is not None:
            return Response(result_string="Job with id %s already exists" % job.uid,
                            is_success=False)
        job.status = JobStatus.QUEUED
        database.update_job(job)
        return Response(result_string="Successfully added job with id: %s" % job.uid,
                        is_success=True, uid=job.uid)
