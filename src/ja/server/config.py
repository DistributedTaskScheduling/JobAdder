from typing import Dict, cast
from ja.common.config import Config
import yaml


def _check_port(port: int) -> None:
    """
    Check if the given port is valid, and raise a ValueError otherwise.
    """
    if port is not None and (port < 1 or port > 65535):
        raise ValueError("Port number must be in range [1, 65535].")


class LoginConfig(Config):
    """
    Config for the database or the email information used on the central server.
    """

    def __init__(self, host: str, port: int, username: str, password: str):
        _check_port(port)
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def __eq__(self, o: object) -> bool:
        if isinstance(o, LoginConfig):
            return self._host == o.host \
                and self._port == o.port \
                and self._username == o.username \
                and self._password == o.password
        else:
            return False

    @property
    def host(self) -> str:
        """!
        @return: Host to connect to access the database.
        """
        return self._host

    @property
    def port(self) -> int:
        """!
        @return: Port to use when accessing the database.
        """
        return self._port

    @property
    def username(self) -> str:
        """!
        @return: Username to use when accessing the database.
        """
        return self._username

    @property
    def password(self) -> str:
        """!
        @return: Password to use when accessing the database.
        """
        return self._password

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["host"] = self._host
        d["port"] = self._port
        d["username"] = self._username
        d["password"] = self._password
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "LoginConfig":
        host = cls._get_str_from_dict(property_dict=property_dict, key="host")
        port = cls._get_int_from_dict(property_dict=property_dict, key="port", mandatory=False)
        username = cls._get_str_from_dict(property_dict=property_dict, key="username")
        password = cls._get_str_from_dict(property_dict=property_dict, key="password")

        cls._assert_all_properties_used(property_dict)
        return LoginConfig(host, port, username, password)


class ServerConfig(Config):
    """
    Config for the central server.
    """

    def __init__(self, admin_group: str, database_config: LoginConfig, email_config: LoginConfig,
                 special_resources: Dict[str, int],
                 blocking_enabled: bool = True, preemption_enabled: bool = True, web_server_port: int = 0):
        self._admin_group = admin_group
        self._database_config = database_config
        self._email_config = email_config
        self._special_resources = special_resources
        self._blocking_enabled = blocking_enabled
        self._preemption_enabled = preemption_enabled
        self._web_server_port = web_server_port

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ServerConfig):
            return self._admin_group == o.admin_group \
                and self._database_config == o.database_config \
                and self._email_config == o.email_config \
                and self._special_resources == o.special_resources \
                and self._blocking_enabled == o.blocking_enabled \
                and self._preemption_enabled == o.preemption_enabled \
                and self._web_server_port == o.web_server_port
        else:
            return False

    @property
    def admin_group(self) -> str:
        """!
        @return: Name of the group of admins.
        """
        return self._admin_group

    @property
    def database_config(self) -> LoginConfig:
        """!
        @return: Config describing parameters for accessing the server database.
        """
        return self._database_config

    @property
    def email_config(self) -> LoginConfig:
        """!
        @return: Config describing email information of the user.
        """
        return self._email_config

    @property
    def special_resources(self) -> Dict[str, int]:
        """!
        Special resources (like software licenses) available on the server. Each special resource is encoded as a
        dictionary entry with a string for the name and an integer for the quantity.
        @return: Special resources available on the server.
        """
        return self._special_resources

    @property
    def blocking_enabled(self) -> bool:
        """!
        True by default.
        @return: If True, enable reserving work machines for jobs with high effective priority.
        """
        return self._blocking_enabled

    @property
    def preemption_enabled(self) -> bool:
        """!
        True by default.
        @return: If True, enable pausing jobs to free up resources for jobs with high effective priority.
        """
        return self._preemption_enabled

    @property
    def web_server_port(self) -> int:
        """!
        The port to listen to for requests to the WebAPI.
        If set to 0, the WebAPI is disabled.

        @return: The port for the WebAPI, or 0 if not enabled.
        """
        return self._web_server_port

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["admin_group"] = self._admin_group
        d["database_config"] = self._database_config.to_dict()
        d["email_config"] = self._email_config.to_dict()
        d["special_resources"] = self._special_resources
        d["blocking_enabled"] = self._blocking_enabled
        d["preemption_enabled"] = self._preemption_enabled
        d["web_server_port"] = self._web_server_port
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "ServerConfig":
        admin_group = cls._get_str_from_dict(property_dict=property_dict, key="admin_group")
        database_config = LoginConfig.from_dict(cls._get_dict_from_dict(property_dict=property_dict,
                                                                        key="database_config"))
        email_config = LoginConfig.from_dict(cls._get_dict_from_dict(property_dict=property_dict, key="email_config"))
        special_resources: Dict[str, int] = cast(Dict[str, int], cls._get_dict_from_dict(property_dict=property_dict,
                                                                                         key="special_resources"))
        blocking_enabled = cls._get_bool_from_dict(property_dict=property_dict, key="blocking_enabled")
        preemption_enabled = cls._get_bool_from_dict(property_dict=property_dict, key="preemption_enabled")
        web_server_port = cls._get_int_from_dict(property_dict=property_dict, key="web_server_port")

        cls._assert_all_properties_used(property_dict)
        return ServerConfig(admin_group, database_config, email_config, special_resources,
                            blocking_enabled, preemption_enabled, web_server_port)

    @classmethod
    def from_string(cls, yaml_string: str) -> "ServerConfig":
        as_dict = yaml.load(yaml_string, Loader=yaml.SafeLoader)
        assert isinstance(as_dict, dict)
        return cls.from_dict(as_dict)
