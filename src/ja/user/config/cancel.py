from ja.user.config.base import UserConfig


class CancelCommandConfig(UserConfig):
    """
    Config for the cancel command of the user client.
    """
    def __init__(self, label: str = None, uid: str = None):
        """!
        Exactly one out of @label and @uid must be set.
        @param label: label of the job(s) to be cancelled.
        @param uid: uid of the job to be cancelled.
        """

    @property
    def label(self) -> str:
        """!
        @return: The label of the job(s) to be cancelled.
        """

    @property
    def uid(self) -> str:
        """!
        @return: The uid of the job to be cancelled.
        """
