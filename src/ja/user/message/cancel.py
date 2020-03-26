from typing import Dict
from ja.user.message.base import UserServerCommand
from ja.common.message.base import Response
from ja.common.job import Job
from ja.server.database.database import ServerDatabase
from ja.user.config.base import UserConfig
from ja.common.job import JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry


class CancelCommand(UserServerCommand):
    """
    Command for canceling a job.
    """

    def __init__(self, config: UserConfig, label: str = None, uid: str = None):
        """!
        @param config: Config to create the cancel command from.
        """
        if label is None and uid is None:
            raise ValueError("One of both uid and label must be set")
        if label is not None and uid is not None:
            raise ValueError("Only one of both uid and label should be set")
        self._config = config
        self._label = label
        self._uid = uid

    def __eq__(self, o: object) -> bool:
        if isinstance(o, CancelCommand):
            return self._config == o._config and self._label == o._label and self._uid == o._uid
        else:
            return False

    @property
    def config(self) -> UserConfig:
        """!
        @return: The UserConfig of this command.
        """
        return self._config

    @property
    def label(self) -> str:
        """!
        @return: The label of the job(s) to be cancelled.
        """
        return self._label

    @property
    def uid(self) -> str:
        """!
        @return: The uid of the job to be cancelled.
        """
        return self._uid

    def to_dict(self) -> Dict[str, object]:
        _dict: Dict[str, object] = dict()
        _dict["label"] = self._label
        _dict["uid"] = self._uid
        _dict["config"] = self._config.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "CancelCommand":
        _label = cls._get_str_from_dict(property_dict=property_dict, key="label", mandatory=False)
        _uid = cls._get_str_from_dict(property_dict=property_dict, key="uid", mandatory=False)
        _config = UserConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="config", mandatory=True))

        cls._assert_all_properties_used(property_dict)
        return CancelCommand(label=_label, uid=_uid, config=_config)

    def _cancel_job(self, database: ServerDatabase, job: Job, ignore_wrong_permissions: bool) -> bool:
        has_permissions = (job.owner_id == self.effective_user or self.effective_user == 0)
        if not has_permissions:
            return ignore_wrong_permissions

        job.status = JobStatus.CANCELLED
        database.update_job(job)
        return True

    def execute(self, database: ServerDatabase) -> Response:
        """!
        Executes this command on the database.
        @return: A Response informing the user if the job was cancelled or not.
        """
        if self.uid is not None:
            job_entry: DatabaseJobEntry = database.find_job_by_id(self.uid)
            if job_entry is None:
                return Response(result_string="Job with uid %s does not exist!" % self.uid,
                                is_success=False)
            else:
                job = job_entry.job
                if job.status in [JobStatus.CRASHED, JobStatus.CANCELLED, JobStatus.DONE]:
                    return Response(result_string="Cannot cancel job with uid: %s as it has crashed or is already done"
                                    % self.uid,
                                    is_success=False)

                if self._cancel_job(database, job, False):
                    return Response(result_string="Successfully cancelled job with uid: %s" % self.uid, is_success=True)
                else:
                    return Response("Insufficient permissions to cancel job with uid: %s" % self.uid, False)

        # Cancel by label
        jobs = database.find_job_by_label(self.label)
        if jobs == []:
            return Response(result_string="No job with label %s exists!" % self.label,
                            is_success=False)
        cancelled: bool = False
        for job in jobs:
            if job.status in [JobStatus.CRASHED, JobStatus.CANCELLED, JobStatus.DONE]:
                continue
            self._cancel_job(database, job, True)
            cancelled = True
        if not cancelled:
            return Response(result_string="No running/paused/queued job with label %s exists!" % self.label,
                            is_success=False)
        return Response(result_string="Successfully cancelled all jobs with label: %s" % self.label, is_success=True)
