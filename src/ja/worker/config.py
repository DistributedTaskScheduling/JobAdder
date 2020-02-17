from typing import Dict
from ja.common.config import Config
from ja.common.proxy.ssh import SSHConfig
from ja.common.work_machine import ResourceAllocation


class WorkerConfig(Config):
    """
    Config for the worker client.
    """

    def __init__(self, uid: str, ssh_config: SSHConfig, resource_allocation: ResourceAllocation):
        """!
        creates resource allocation instance
        """
        self._uid = uid
        self._ssh_config = ssh_config
        self._resource_allocation = resource_allocation

    @property
    def uid(self) -> str:
        """!
        @return: The desired UID to register with on the server.
        """
        return str(self._uid)

    @property
    def ssh_config(self) -> SSHConfig:
        """!
        @return: Parameters for establishing an ssh connection to the server.
        """
        return self._ssh_config

    @property
    def resources(self) -> ResourceAllocation:
        """!
        @return: The resources available on this work machine.
        """
        return self._resource_allocation

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["ssh_config"] = self._ssh_config.to_dict()
        d["resource_allocation"] = self._resource_allocation.to_dict()
        d["uid"] = self._uid
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerConfig":
        ssh_config = SSHConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="ssh_config", mandatory=False))
        resource_allocation = ResourceAllocation.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="resource_allocation", mandatory=False))
        uid = str(property_dict["uid"])
        return WorkerConfig(uid, ssh_config, resource_allocation)
