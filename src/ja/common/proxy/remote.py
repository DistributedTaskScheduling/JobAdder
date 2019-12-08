from abc import ABC


class Remote(ABC):
    """
    Abstract base class for remote objects accessed by Proxy objects.
    Remotes are single-class command line programs.

    Remotes receive a Message object represented by a YAML string on stdin.
    Remotes then convert the YAML string to a Message object. Remotes then pass
    on the Message object to a MessageHandler object via a socket. Remotes then
    listen for a response (YAML string) on a socket. The response is then
    written to stdout.
    """
