from abc import ABC


class CommandHandler(ABC):
    """
    Abstract base class that handles Commands received by Remote objects.
    Commands are transferred from Remote to MessageHandler by socket as YAML
    string. Once initialized, continuously listens for Commands.
    When a Command is received it is validated syntactically first: the
    CommandHandler tries to construct a Command of the correct type from the
    YAML string.
    Afterwards the Command is validated semantically: the CommandHandler checks
    if the user has the necessary permissions to perform the Command, if any
    specified objects actually exist, etc.
    If both validations pass, the Command is executed.
    Always prints back a Response as YAML string to the socket at the end. The
    success property of the Response is True if both validations were passed
    and the Command was executed without error, and is false otherwise.
    """
    def __init__(self, socket: str):
        """!
        @param socket: The Unix named socket to listen for Commands on.
        """
