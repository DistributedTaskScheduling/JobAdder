from typing import Dict
from ja.common.message.server import ServerCommand
from ja.common.message.base import Response
from ja.server.database.database import ServerDatabase
from ja.user.config.base import UserConfig
from ja.common.job import Job, JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry


class CancelCommand(ServerCommand):
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

    def execute(self, database: ServerDatabase) -> Response:
        """!
        Executes this command on the database.
        @return: A Response informing the user if the job was cancelled or not.
        """
        job: Job = None
        if self.uid is not None:
            job_entry: DatabaseJobEntry = database.find_job_by_id(self.uid)
            if job_entry is None:
                return Response(result_string="Job with uid %s does not exist!" % self.uid,
                                is_success=False)
            else:
                job = job_entry.job
        if self.label is not None:
            job = database.find_job_by_label(self.label)
            if job is None:
                return Response(result_string="Job with label %s does not exist!" % self.label,
                                is_success=False)
        if job.owner_id != self.config.ssh_config.username:  # Might not be the right way to verify a user.
            if self.label is not None:
                return Response(result_string="You do not have the permission to cancel the job with label %s"
                                % self.label, is_success=False)
            else:
                return Response(result_string="You do not have the permission to cancel the job with uid %s"
                                % self.uid, is_success=False)

        job.status = JobStatus.CANCELLED
        database.update_job(job)
        if self.uid is not None:
            return Response(result_string="Successfully removed job with uid: %s" % self.uid,
                            is_success=True)
        if self.label is not None:
            return Response(result_string="Successfully removed job with label: %s" % self.label,
                            is_success=True)
        return Response("Unreachable code.", is_success=False)
