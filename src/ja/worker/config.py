from typing import Dict
from ja.common.config import Config
from ja.common.proxy.ssh import SSHConfig
from ja.common.work_machine import ResourceAllocation


class WorkerConfig(Config):
    """
    Config for the worker client.
    """

    def __init__(self, uid: str, ssh_config: SSHConfig, resource_allocation: ResourceAllocation, admin_group: str):
        """!
        creates resource allocation instance
        """
        if ssh_config is None:
            raise ValueError("the WorkerConfig class is missing the ssh_config param and it cannot be None!")
        if resource_allocation is None:
            raise ValueError("the WorkerConfig class is missing the ressource_allocation param and it cannot be None")

        self._ssh_config = ssh_config
        self._resource_allocation = resource_allocation
        self._uid = uid
        self._admin_group = admin_group

    def __eq__(self, o: object) -> bool:
        if isinstance(o, WorkerConfig):
            return self._ssh_config == o._ssh_config \
                and self._uid == o._uid \
                and self._resource_allocation == o._resource_allocation
        else:
            return False

    @property
    def uid(self) -> str:
        """!
        @return: The desired UID to register with on the server.
        """
        return str(self._uid)

    @uid.setter
    def uid(self, new_uid: str) -> None:
        self._uid = new_uid

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

    @property
    def admin_group(self) -> str:
        """!
        @return: Name of the group of admins.
        """
        return self._admin_group

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = dict()
        d["ssh_config"] = self._ssh_config.to_dict()
        d["resource_allocation"] = self._resource_allocation.to_dict()
        d["uid"] = self._uid
        d["admin_group"] = self.admin_group
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerConfig":
        ssh_config = SSHConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="ssh_config", mandatory=True))
        resource_allocation = ResourceAllocation.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="resource_allocation", mandatory=True))
        uid = cls._get_str_from_dict(property_dict, "uid", mandatory=False)
        admin_group = cls._get_str_from_dict(property_dict, "admin_group", mandatory=True)
        cls._assert_all_properties_used(property_dict)
        return WorkerConfig(uid, ssh_config, resource_allocation, admin_group)
