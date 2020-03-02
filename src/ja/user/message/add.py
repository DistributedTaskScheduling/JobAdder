from typing import Dict
from ja.common.message.server import ServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.user.config.add import AddCommandConfig
from ja.common.job import Job, JobStatus


class AddCommand(ServerCommand):
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
        db_job: Job = database.find_job_by_id(job.uid)
        if db_job is not None:
            return Response(result_string="Job with id %s already exists" % job.uid,
                            is_success=False)
        db_job: Job = database.find_job_by_label(job.label)
        if db_job is not None:
            return Response(result_string="Job with label %s already exists" % job.label,
                            is_success=False)
        job.status = JobStatus.QUEUED
        database.update_job(job)
        return Response(result_string="Successfully added job with id: %s" % job.uid,
                        is_success=True, uid=job.uid)
