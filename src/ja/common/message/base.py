"""
The Message module provides the necessary interfaces that have to be
implemented in order for a class to be transferable between the components
of JobAdder.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, cast
import yaml


class Serializable(ABC):
    """
    A base class for all objects which can be converted to and from a Python
    dictionary. The dictionary should contain only basic python types:
    strings, ints, bytes, doubles, lists and dictionaries. The dictionary can
    also be dumped as/read from a YAML string.
    """

    @classmethod
    def _get_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> object:
        _property = property_dict.pop(key, None)
        if mandatory and _property is None:
            raise ValueError(
                "Cannot read in object of type %s because the dictionary does not have the mandatory property %s"
                % (cls, key)
            )
        return _property

    @classmethod
    def _raise_error_wrong_type(cls, key: str, expected_type: str, actual_type: str) -> None:
        raise ValueError(
            "Cannot read in object of type %s. Expected type of property %s to be %s but received %s"
            % (cls.__name__, key, expected_type, actual_type)
        )

    @classmethod
    def _assert_all_properties_used(cls, property_dict: Dict[str, object]) -> None:
        if property_dict:
            raise ValueError(
                "Received unexpected properties %s when reading in an object of type %s"
                % (property_dict.keys(), cls.__name__)
            )

    @classmethod
    def _get_dict_from_dict(
            cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> Dict[str, object]:
        _property = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if not isinstance(_property, dict):
            cls._raise_error_wrong_type(key=key, expected_type="dict", actual_type=_property.__class__.__name__)
        return cast(Dict[str, object], _property)

    @classmethod
    def _get_str_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> str:
        _property = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if not isinstance(_property, str):
            cls._raise_error_wrong_type(key=key, expected_type="str", actual_type=_property.__class__.__name__)
        return cast(str, _property)

    @classmethod
    def _get_str_list_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> List[str]:
        _property = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if not isinstance(_property, list):
            cls._raise_error_wrong_type(key=key, expected_type="List[str]", actual_type=_property.__class__.__name__)
        _list = cast(List[object], _property)
        for _element in _list:
            if not isinstance(_element, str):
                cls._raise_error_wrong_type(key=key, expected_type="List[str]", actual_type="List[object]")
        return cast(List[str], _list)

    @classmethod
    def _get_int_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> int:
        _property = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if not isinstance(_property, int):
            cls._raise_error_wrong_type(key=key, expected_type="int", actual_type=_property.__class__.__name__)
        return cast(int, _property)

    @classmethod
    def _get_bool_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> bool:
        _property = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if not isinstance(_property, bool):
            cls._raise_error_wrong_type(key=key, expected_type="int", actual_type=_property.__class__.__name__)
        return cast(bool, _property)

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
        as_yaml = yaml.dump(self.to_dict())
        assert isinstance(as_yaml, str)
        return as_yaml

    @classmethod
    def from_string(cls, yaml_string: str) -> "Serializable":
        """!
        @param yaml_string A YAML document (string) defining the desired
        properties of the Serializable object to be created.
        @return A new Serializable object based on the properties encoded in
        the YAML document.
        """
        as_dict = yaml.load(yaml_string, Loader=yaml.SafeLoader)
        assert isinstance(as_dict, dict)
        return cls.from_dict(as_dict)


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
