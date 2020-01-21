from ja.common.message.base import Serializable
from typing import Dict
from unittest import TestCase


class SimpleSerializable(Serializable):
    def __init__(self, x: int) -> None:
        self.x = x

    def to_dict(self) -> Dict[str, object]:
        return {'x': self.x}

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "SimpleSerializable":
        assert len(property_dict) == 1
        assert 'x' in property_dict
        assert isinstance(property_dict['x'], int)
        return SimpleSerializable(property_dict['x'])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimpleSerializable):
            return False

        return self.x == other.x


class SerializableTest(TestCase):
    def test_simple_serializable(self) -> None:
        simple5 = SimpleSerializable(5)
        self.assertEqual(simple5, SimpleSerializable.from_string(str(simple5)))

        string_repr = 'x: 5'
        self.assertEqual(SimpleSerializable.from_string(string_repr), simple5)
