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

    @property
    def verbosity(self) -> Verbosity:
        """!
        @return: The verbosity level with which to print out information.
        """

    @property
    def ssh_config(self) -> SSHConfig:
        """!
        @return: The config containing the parameters for establishing an ssh connection to the server.
        """

    def source_from_user_config(self, other_config: "UserConfig", unset_only: bool = True) -> None:
        """!
        Source the properties of this object from another UserConfig object.
        @param other_config: The config whose values to source from.
        @param unset_only: If True, only source values which have not been set for this object.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "UserConfig":
        pass

    def override(self, other_config: "UserConfig", unset_only: bool = True) -> None:
        pass
