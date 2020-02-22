from ja.common.job import JobPriority, JobStatus
from ja.common.proxy.ssh import SSHConfig
from test.serializable.base import AbstractSerializableTest

from typing import List
from datetime import datetime, timedelta

from ja.user.message.query import QueryCommand
from ja.user.config.base import UserConfig, Verbosity


class QueryCommandTest(AbstractSerializableTest):
    """
    Class for testing QueryCommandConfig.
    """

    def setUp(self) -> None:
        time_now = datetime.now().strftime(QueryCommand.datetime_format)
        time_now_datetime = datetime.strptime(time_now, time_now)
        config = UserConfig(
            ssh_config=SSHConfig(
                hostname="ies", username="pettto", password="1234567890", key_filename="~/.ssh/id_rsa"),
            verbosity=Verbosity.DETAILED)
        self._object = QueryCommand(config=config, uid=["asdf", "sdf"], label=["fqwe", "dalfs"], owner=["safd", "sad"],
                                    priority=[JobPriority.HIGH],
                                    status=[JobStatus.CRASHED],
                                    is_preemptible=True, special_resources=[["abc", "bcd"], ["ops", "123"]],
                                    cpu_threads=(1, 2), memory=(2000, 3000),
                                    before=time_now_datetime + timedelta(hours=2), after=time_now_datetime)
        v_list: List[str] = list(QueryCommand.__dir__(self._object))
        self._optional_properties = [a[1:] for a in v_list]
        self._object_dict = {
            "uid": ["asdf", "sdf"],
            "label": ["fqwe", "dalfs"],
            "owner": [1000, 2000],
            "priority": [2],
            "status": [6],
            "is_preemptible": True,
            "special_resources": [["abc", "bcd"], ["ops", "123"]],
            "cpu_threads": (1, 2),
            "memory": (2000, 3000),
            "after": time_now_datetime.strftime(QueryCommand.datetime_format),
            "before": (time_now_datetime + timedelta(hours=2)).strftime(QueryCommand.datetime_format),
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "ies",
                    "username": "pettto",
                    "password": "1234567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            }
        }

        self._other_object_dict = {
            "uid": ["adlfjs", "alsfjslkfj"],
            "label": ["fqwe", "lasjdfafj"],
            "owner": [3, 4],
            "priority": [2],
            "status": [6],
            "is_preemptible": True,
            "special_resources": [["bc", "bcd"], ["ops", "123"]],
            "cpu_threads": (1, 2),
            "memory": (200, 300),
            "after": time_now_datetime.strftime(QueryCommand.datetime_format),
            "before": (time_now_datetime + timedelta(hours=2)).strftime(QueryCommand.datetime_format),
            "config": {
                "verbosity": 2,
                "ssh_config": {
                    "hostname": "ies",
                    "username": "pettto",
                    "password": "1234567890",
                    "passphrase": None,
                    "key_filename": "~/.ssh/id_rsa"
                }
            }
        }
