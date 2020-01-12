from typing import Dict

from ja.common.config import Config


class DatabaseConfig(Config):
    """
    Config for the database used on the central server.
    """

    @property
    def host(self) -> str:
        """!
        @return: Host to connect to access the database.
        """

    @property
    def port(self) -> int:
        """!
        @return: Port to use when accessing the database.
        """

    @property
    def username(self) -> str:
        """!
        @return: Username to use when accessing the database.
        """

    @property
    def password(self) -> str:
        """!
        @return: Password to use when accessing the database.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "DatabaseConfig":
        pass


class ServerConfig(Config):
    """
    Config for the central server.
    """

    @property
    def database_config(self) -> DatabaseConfig:
        """!
        @return: Config describing parameters for accessing the server database.
        """

    @property
    def special_resources(self) -> Dict[str, int]:
        """!
        Special resources (like software licenses) available on the server. Each special resource is encoded as a
        dictionary entry with a string for the name and an integer for the quantity.
        @return: Special resources available on the server.
        """

    @property
    def blocking_enabled(self) -> bool:
        """!
        True by default.
        @return: If True, enable reserving work machines for jobs with high effective priority.
        """

    @property
    def preemption_enabled(self) -> bool:
        """!
        True by default.
        @return: If True, enable pausing jobs to free up resources for jobs with high effective priority.
        """

    @property
    def web_server_enabled(self) -> bool:
        """!
        True by default.
        @return: If True, enable the web server.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ServerConfig":
        pass
