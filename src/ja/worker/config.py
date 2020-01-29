from typing import Dict

from ..common.config import Config
from ..common.proxy.ssh import SSHConfig
from ..common.work_machine import ResourceAllocation
import yaml
import os
import psutil



class WorkerConfig(Config):
    """
    Config for the worker client.
    """

    def __init__(self, conf_path: str):
        """!
        reads the config file from the disk
        creates resource allocation instance
        """
        self._conf_path = conf_path
        self._ssh_config = self.read_conf()
        self._resource_allocation = self.get_resources()

    def read_conf(self) -> SSHConfig:
        with open(self._conf_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        hostname: str = data_loaded["hostname"]
        username: str = data_loaded["username"]
        self._uid = data_loaded["uid"]
        return SSHConfig(hostname = hostname, username = username)
        
    def get_resources(self) -> ResourceAllocation:
        cpu_threads = os.cpu_count()
        mem = psutil.virtual_memory().available
        swap = 0.5 * mem 
        return ResourceAllocation(cpu_threads, mem, swap)

    @property
    def uid(self) -> str:
        """!
        @return: The desired UID to register with on the server.
        """
        return self._uid

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
        #the sshconfig.to_dict() needs to be implemented
        d["ssh_config"] = self._ssh_config.to_dict()
        d["resource_allocation"] = self._resource_allocation.to_dict()
        d["uid"] = self._uid
        return d

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerConfig":
        #_ssh_config = SSHConfig.from_dict(
        #    cls._get_dict_from_dict(property_dict=property_dict, key="ssh_config", mandatory=False))
        #_resource_allocation = ResourceAllocation.from_dict(
        #    cls._get_dict_from_dict(property_dict=property_dict, key="resource_allocation", mandatory=False))
        #_uid = str(property_dict["uid"])
        #return WorkerConfig(_uid, _ssh_config, _resource_allocation)
        pass
