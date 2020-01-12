from ja.common.message.server import ServerCommand


class UserClientCLIHandler:
    """
    Class for handling user input on the user client.
    """
    def __init__(self, config_path: str):
        """!
        Loads a general user client config file from the disk.
        @param config_path: The path to load a general config from.
        """

    def get_server_command(self) -> ServerCommand:
        """!
        Transforms command line arguments into a UserConfig object. Creates and returns a ServerCommand object from the
        command line arguments combined with the general config loaded in the constructor.
        @return: The ServerCommand created from the combined input.
        """
