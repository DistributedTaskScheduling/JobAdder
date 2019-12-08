class UserClientCLIHandler:
    """
    Class for handling user input on the user client. Transforms command line
    arguments into a UserConfig object. Loads user client config files from the
    disk. Creates ServerCommand objects from the unified configs.
    """
