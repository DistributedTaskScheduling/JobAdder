from ja.common.message.server import ServerCommand


class UserServerCommand(ServerCommand):
    def __init__(self) -> None:
        self._effective_user: int = -1

    @property
    def effective_user(self) -> int:
        return self._effective_user

    @effective_user.setter
    def effective_user(self, user: int) -> None:
        self._effective_user = user
