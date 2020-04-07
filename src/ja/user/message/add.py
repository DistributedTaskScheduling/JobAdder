from copy import deepcopy
from typing import Dict
from ja.user.message.base import UserServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.user.config.add import AddCommandConfig
from ja.common.job import Job, JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry

import logging
logger = logging.getLogger(__name__)


class AddCommand(UserServerCommand):
    """
    Command for adding a job.
    """
    def __init__(self, config: AddCommandConfig):
        """!
        @param config: Config to create the add command from.
        """
        super().__init__(config=config)

    @property
    def config(self) -> AddCommandConfig:
        """!
        @return the AddCommandConfig for this Command.
        """
        return self._config  # type: ignore

    def to_dict(self) -> Dict[str, object]:
        return self._config.to_dict()

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "AddCommand":
        return AddCommand(AddCommandConfig.from_dict(property_dict))

    def execute(self, database: ServerDatabase) -> Response:
        job: Job = self.config.job
        if job.owner_id == -1:
            job.owner_id = self.effective_user

        if not self.effective_user_is_root and self.effective_user != job.owner_id:
            return Response(result_string="Cannot submit jobs for other users.", is_success=False)

        db_job_id: DatabaseJobEntry = database.find_job_by_id(job.uid)
        if db_job_id is not None:
            return Response(result_string="Job with id %s already exists" % job.uid,
                            is_success=False)

        max_sr = database.max_special_resources
        if max_sr is None:
            max_sr = dict()
        available_sr = deepcopy(max_sr)
        for sr in job.scheduling_constraints.special_resources:
            sr_count = available_sr.pop(sr, 0)
            if sr_count <= 0:
                return Response(
                    result_string="Cannot add job because the server is lacking special resource %s (%s "
                                  "available)." % (sr, max_sr.get(sr, 0)),
                    is_success=False)
            available_sr[sr] = sr_count - 1

        if job.status == JobStatus.NEW:
            job.status = JobStatus.QUEUED
        job.uid = database.update_job(job)
        logger.debug(str(job))
        return Response(result_string="Successfully added job with id: %s" % job.uid,
                        is_success=True, uid=job.uid)
