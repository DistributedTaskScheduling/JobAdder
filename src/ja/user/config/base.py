from enum import Enum
from typing import Dict
from ja.common.config import Config
from ja.common.proxy.ssh import SSHConfig


class Verbosity(Enum):
    """
    Represents the verbosity level with which to print out information for commands sent by the user to the server.
    """
    NONE = 0
    HIGH_LEVEL = 1
    DETAILED = 2


class UserConfig(Config):
    """
    Base class for user client Config classes.
    """

    def __init__(self, ssh_config: SSHConfig = None, verbosity: Verbosity = None) -> None:
        self._verbosity = verbosity
        self._ssh_config = ssh_config

    def __eq__(self, o: object) -> bool:
        if isinstance(o, UserConfig):
            return self.verbosity == o.verbosity and self.ssh_config == o.ssh_config
        else:
            return False

    @property
    def verbosity(self) -> Verbosity:
        """!
        @return: The verbosity level with which to print out information.
        """
        return self._verbosity

    @property
    def ssh_config(self) -> SSHConfig:
        """!
        @return: The config containing the parameters for establishing an ssh connection to the server.
        """
        return self._ssh_config

    def source_from_user_config(self, other_config: "UserConfig", unset_only: bool = True) -> None:
        """!
        Source the properties of this object from another UserConfig object.
        @param other_config: The config whose values to source from.
        @param unset_only: If True, only source values which have not been set for this object.
        """
        if getattr(self, "_ssh_config") is None or unset_only:
            setattr(self, "_ssh_config", getattr(other_config, "_ssh_config"))
        if getattr(self, "_verbosity") is None or unset_only:
            setattr(self, "_verbosity", getattr(other_config, "_verbosity"))

    def to_dict(self) -> Dict[str, object]:
        property_dict: Dict[str, object] = dict()
        property_dict["ssh_config"] = self._ssh_config.to_dict()
        property_dict["verbosity"] = self._verbosity.value
        return property_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "UserConfig":
        ssh_config = SSHConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="ssh_config", mandatory=True))
        verbosity = Verbosity(cls._get_from_dict(property_dict=property_dict, key="verbosity", mandatory=True))
        cls._assert_all_properties_used(property_dict)
        return UserConfig(ssh_config=ssh_config, verbosity=verbosity)
