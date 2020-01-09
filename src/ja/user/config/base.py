from enum import Enum
from typing import Dict

from ja.common.config import Config


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
    def server(self) -> str:
        """!
        @return: The IP address of the server to connect to.
        """

    @property
    def username(self) -> str:
        """!
        @return: The username to use for SSH authentication.
        """

    @property
    def password(self) -> str:
        """!
        @return: The password to use for SSH authentication.
        """

    @property
    def private_key(self) -> str:
        """!
        @return: The private key to use for SSH authentication.
        """

    @property
    def passphrase(self) -> str:
        """!
        @return: The passphrase to use for unlocking the private key for SSH authentication.
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
