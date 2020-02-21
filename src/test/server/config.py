from test.serializable.base import AbstractSerializableTest
from ja.server.config import ServerConfig, LoginConfig


class ServerConfigTest(AbstractSerializableTest):
    """
    Class for testing ServerConfig.
    """
    def setUp(self) -> None:
        self._optional_properties = []

        database_config: LoginConfig = LoginConfig("database-host", 8090, "db-sam", "0000")
        email_config: LoginConfig = LoginConfig("email-host", 25, "friendly-user", "Password")
        self._object: ServerConfig = ServerConfig("techfa", database_config, email_config,
                                                  special_resources={"lic": 4, "bloke": 5},
                                                  blocking_enabled=False)

        self._object_dict = {"admin_group": "techfa",
                             "database_config":
                             {"host": "database-host",
                              "port": 8090,
                              "username": "db-sam",
                              "password": "0000"},
                             "email_config":
                             {"host": "email-host",
                              "port": 25,
                              "username": "friendly-user",
                              "password": "Password"},
                             "special_resources":
                             {"lic": 4, "bloke": 5},
                             "blocking_enabled": False,
                             "preemption_enabled": True,
                             "web_server_enabled": True}
        self._other_object_dict = {"admin_group": "kit",
                                   "database_config":
                                   {"host": "database-host23",
                                    "port": 8091,
                                    "username": "db-fevfre",
                                    "password": "1111"},
                                   "email_config":
                                   {"host": "email-host23",
                                    "port": 26,
                                    "username": "unfriendly-user",
                                    "password": "Password23"},
                                   "special_resources":
                                   {"lic45": 3, "bloke23": 5},
                                   "blocking_enabled": True,
                                   "preemption_enabled": True,
                                   "web_server_enabled": False}
