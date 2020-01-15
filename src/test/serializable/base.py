from copy import deepcopy
from unittest import TestCase
from typing import Dict, List

from ja.common.message.base import Serializable
from test.abstract import skipIfAbstract


class AbstractSerializableTest(TestCase):
    """
    Abstract base class for testing sub-classes of Serializable.
    """
    def setUp(self) -> None:
        self._object: Serializable = None
        self._object_dict: Dict[str, object] = None
        self._other_object_dict: Dict[str, object] = None
        self._optional_properties: List[str] = None

    @skipIfAbstract
    def test_roundtrip(self) -> None:
        property_dict = self._object.to_dict()
        recreated_object = self._object.__class__.from_dict(property_dict)
        self.assertTrue(
            self._object == recreated_object,
            msg="Roundtrip failed for %s: recreated object not equal." % self._object.__class__.__name__
        )

    @skipIfAbstract
    def test_from_dict(self) -> None:
        read_object = self._object.__class__.from_dict(self._object_dict)
        self.assertTrue(
            self._object == read_object,
            msg="Reading in object failed for %s: read in object not equal." % self._object.__class__.__name__
        )

    @skipIfAbstract
    def test_from_other_dict(self) -> None:
        read_object = self._object.__class__.from_dict(self._object_dict)
        other_read_object = self._object.__class__.from_dict(self._other_object_dict)
        self.assertFalse(
            read_object == other_read_object,
            msg="Reading in different objects failed for %s: read in objects are the same."
                % self._object.__class__.__name__
        )

    @skipIfAbstract
    def test_removing_property_raises_error(self) -> None:
        for key in list(self._object_dict.keys()):
            object_dict_copy = deepcopy(self._object_dict)
            object_dict_copy.pop(key)
            if key in self._optional_properties:
                self._object.__class__.from_dict(object_dict_copy)
            else:
                with self.assertRaises(ValueError):
                    self._object.__class__.from_dict(object_dict_copy)

    @skipIfAbstract
    def test_adding_property_raises_error(self) -> None:
        self._object_dict["AYY"] = "LAMO"
        with self.assertRaises(ValueError):
            self._object.__class__.from_dict(self._object_dict)


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
