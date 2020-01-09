from ja.user.config.base import UserConfig
from ja.common.job import Job


class AddCommandConfig(UserConfig):
    """
    Config for the add command of the user client.
    """

    @property
    def job(self) -> Job:
        """!
        @return: The job to be added.
        """

    @property
    def attach(self) -> bool:
        """!
        @return: If True, print output on the command line and only return when the job has finished.
        """

    @property
    def blocking(self) -> bool:
        """!
        @return: If True, only return when once job has finished but do not print output on the command line.
        """
