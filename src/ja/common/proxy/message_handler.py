from abc import ABC


class MessageHandler(ABC):
    """
    Abstract base class that handles Messages received by Remote objects.
    Messages are transferred from Remote to MessageHandler by socket.
    """
