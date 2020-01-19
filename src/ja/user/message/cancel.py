from typing import Dict

from ja.common.message.server import ServerCommand, ServerResponse
from ja.server.database.database import ServerDatabase
from ja.user.config.base import UserConfig


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

    def execute(self, database: ServerDatabase) -> ServerResponse:
        pass
