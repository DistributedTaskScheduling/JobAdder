from typing import Dict

from ja.common.config import Config
from ja.common.proxy.ssh import SSHConfig
from ja.common.work_machine import ResourceAllocation


class WorkerConfig(Config):
    """
    Config for the worker client.
    """

    @property
    def ssh_config(self) -> SSHConfig:
        """!
        @return: Parameters for establishing an ssh connection to the server.
        """

    @property
    def resources(self) -> ResourceAllocation:
        """!
        @return: The resources available on this work machine.
        """

    def to_dict(self) -> Dict[str, object]:
        pass

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "WorkerConfig":
        pass
