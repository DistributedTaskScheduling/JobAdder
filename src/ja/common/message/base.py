"""
The Message module provides the necessary interfaces that have to be
implemented in order for a class to be transferable between the components
of JobAdder.
"""
from abc import ABC, abstractmethod
from typing import Dict


class Serializable(ABC):
    """
    A base class for all objects which can be converted to and from a Python
    dictionary. The dictionary should contain only basic python types:
    strings, ints, bytes, doubles, lists and dictionaries. The dictionary can
    also be dumped as/read from a YAML string.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, object]:
        """!
        @return A dictionary representation of this object.The entries in the
        dictionary are equivalent to the properties of this object.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "Serializable":
        """!
        @param property_dict A Python dictionary defining the desired
        properties of the Serializable object to be created.
        @return A new Serializable object based on the property entries of the
        specified dictionary.
        """

    def __str__(self) -> str:
        """!
        @return A YAML document (string) representation of this object.
        """

    @classmethod
    def from_string(cls, yaml_string: str) -> "Serializable":
        """!
        @param yaml_string A YAML document (string) defining the desired
        properties of the Serializable object to be created.
        @return A new Serializable object based on the properties encoded in
        the YAML document.
        """


class Message(Serializable, ABC):
    """
    A base class for all messages which can be transferred between the
    components of JobAdder.
    """


class Command(Message, ABC):
    """
    A base class for messages which are sent with the intent of performing an
    action on the remote component.
    """

    @property
    def username(self) -> str:
        """!
        @return The name of the user sending the Command.
        """


class Response(Message, ABC):
    """
    A base class for messages which are sent as a response to Commands. They
    indicate the result of the action on the remote component.
    """

    @property
    @abstractmethod
    def result_string(self) -> str:
        """!
        @return A human-readable string that states the result of the sent
        Command.
        """

    @property
    @abstractmethod
    def is_success(self) -> bool:
        """!
        @return Whether the sent Command was successful.
        """
