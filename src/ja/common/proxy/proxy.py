from abc import ABC


class Proxy(ABC):
    """
    Abstract base class that gives remote access to another object (proxy
    design pattern). Communication is done via Message objects. Proxy first
    sends a Command object to Remote. Proxy then receives a Response object
    from Remote to determine the result of the Command message.
    """


class SingleMessageProxy(Proxy):
    """
    Abstract base class for proxies that create a new SSHConnection object for
    each Message sent. SSHConnection objects are automatically closed after the
    Message object is sent.
    """


class ContinuousProxy(Proxy):
    """
    Abstract base class for proxies that immediately establish an
    SSHConnection. Multiple Message objects can be sent via the SSHConnection.
    The SSHConnection remains open until manually closed.
    """
