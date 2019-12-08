"""
The Message module provides the necessary interfaces that have to be
implemented in order for a class to be transferable between the components
of JobAdder.
"""
from abc import ABC


class Serializable(ABC):
    """
    A base class for all objects which can be converted to and from a python
    dictionary. The dictionary should contain only basic python types:
    strings, ints, bytes, doubles, lists and dictionaries.
    """


class Message(Serializable):
    """
    A base class for all messages which can be transferred between the
    components of JobAdder.
    """
