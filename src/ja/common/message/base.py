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
        prop = property_dict.pop(key, None)
        if mandatory and prop is None:
            raise ValueError(
                "Cannot read in object of type %s because the dictionary does not have the mandatory property %s"
                % (cls, key)
            )
        return prop

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
        prop = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if mandatory and not isinstance(prop, dict):
            cls._raise_error_wrong_type(key=key, expected_type="dict", actual_type=prop.__class__.__name__)
        return cast(Dict[str, object], prop)

    @classmethod
    def _get_str_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> str:
        prop = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if mandatory and not isinstance(prop, str):
            cls._raise_error_wrong_type(key=key, expected_type="str", actual_type=prop.__class__.__name__)
        return cast(str, prop)

    @classmethod
    def _get_str_list_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> List[str]:
        prop = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if mandatory and not isinstance(prop, list):
            cls._raise_error_wrong_type(key=key, expected_type="List[str]", actual_type=prop.__class__.__name__)
        return_list = cast(List[object], prop)
        for element in return_list:
            if not isinstance(element, str):
                cls._raise_error_wrong_type(key=key, expected_type="List[str]", actual_type="List[object]")
        return cast(List[str], return_list)

    @classmethod
    def _get_int_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> int:
        prop = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if mandatory and not isinstance(prop, int):
            cls._raise_error_wrong_type(key=key, expected_type="int", actual_type=prop.__class__.__name__)
        return cast(int, prop)

    @classmethod
    def _get_bool_from_dict(cls, property_dict: Dict[str, object], key: str, mandatory: bool = True) -> bool:
        prop = cls._get_from_dict(property_dict=property_dict, key=key, mandatory=mandatory)
        if mandatory and not isinstance(prop, bool):
            cls._raise_error_wrong_type(key=key, expected_type="int", actual_type=prop.__class__.__name__)
        return cast(bool, prop)

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


class Response(Message):
    """
    A base class for messages which are sent as a response to Commands. They
    indicate the result of the action on the remote component.
    """
    def __init__(self, result_string: str, is_success: bool, uid: str = None):
        self._result_string = result_string
        self._is_success = is_success
        self._uid = uid

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.result_string == other.result_string \
                and self.is_success == other.is_success \
                and self.uid == other.uid
        else:
            return False

    @property
    def result_string(self) -> str:
        """!
        @return A human-readable string that states the result of the sent
        Command.
        """
        return self._result_string

    @property
    def is_success(self) -> bool:
        """!
        @return Whether the sent Command was successful.
        """
        return self._is_success

    @property
    def uid(self) -> str:
        """!
        @return: UID of an added job/registered worker, None otherwise.
        """
        return self._uid

    def to_dict(self) -> Dict[str, object]:
        return {"result_string": self.result_string, "is_success": self.is_success, "uid": self.uid}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "Response":
        result_string = cls._get_str_from_dict(property_dict=property_dict, key="result_string")
        is_success = cls._get_bool_from_dict(property_dict=property_dict, key="is_success")
        uid = cls._get_str_from_dict(property_dict=property_dict, key="uid", mandatory=False)
        cls._assert_all_properties_used(property_dict)
        return cls(result_string=result_string, is_success=is_success, uid=uid)
