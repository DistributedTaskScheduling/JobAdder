from abc import ABC

from ja.common.message.server import ServerCommand
from ja.user.config.base import UserConfig


class UserServerCommand(ServerCommand, ABC):
    def __init__(self, config: UserConfig) -> None:
        self._effective_user: int = 0
        self._config = config

    @property
    def effective_user(self) -> int:
        return self._effective_user

    @effective_user.setter
    def effective_user(self, user: int) -> None:
        self._effective_user = user

    @property
    def config(self) -> UserConfig:
        return self._config
