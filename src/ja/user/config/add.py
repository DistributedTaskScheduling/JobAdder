from typing import Dict, Iterable

from ja.user.config.base import UserConfig
from ja.common.job import Job


class AddCommandConfig(UserConfig):
    """
    Config for the add command of the user client.
    """

    def __init__(self, config: UserConfig,
                 job: Job = None, blocking: bool = True):
        super().__init__(ssh_config=config.ssh_config, verbosity=config.verbosity)
        self._job = job
        self._blocking = blocking

    @property
    def job(self) -> Job:
        """!
        @return: The job to be added.
        """
        return self._job

    @property
    def blocking(self) -> bool:
        """!
        @return: If True, only return when once job has finished but do not print output on the command line.
        """
        return self._blocking

    def __dir__(self) -> Iterable[str]:
        return ["_blocking", "_attach", "_job", "_ssh_config", "_verbosity"]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, AddCommandConfig):
            return self._job == o._job \
                and self._blocking == o._blocking \
                and self._ssh_config == o._ssh_config and self._verbosity == o._verbosity
        else:
            return False

    def source_from_add_config(self, other_config: "AddCommandConfig", unset_only: bool = True) -> None:
        for attr in dir(self):
            if getattr(self, attr) is None or unset_only:
                setattr(self, attr, getattr(other_config, attr))

    def to_dict(self) -> Dict[str, object]:
        add_dict: Dict[str, object] = dict()
        add_dict["config"] = super().to_dict()
        add_dict["job"] = self.job.to_dict()
        add_dict["blocking"] = self._blocking
        return add_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "AddCommandConfig":
        if "job" in property_dict:
            job = Job.from_dict(cls._get_dict_from_dict(property_dict=property_dict, key="job", mandatory=False))
        else:
            job = None
        blocking = cls._get_bool_from_dict(property_dict=property_dict, key="blocking", mandatory=False)
        config = UserConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="config", mandatory=True))
        cls._assert_all_properties_used(property_dict)
        return AddCommandConfig(config, job, blocking)
