import unittest

from hikerservespacecraft import materials
from hikerservespacecraft.utils.serialization import serialize, deserialize2, SerializationError, DeserializationError
from hikerservespacecraft.spacecraft import Spacecraft
from hikerservespacecraft.hull import Hull



class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.hull1 = Hull(materials['Titanium'], 50, "Main Hull", [1000, 500, 300])
        self.hull2 = Hull(materials['Aluminum'], 30, "Secondary Hull", [800, 400, 200])
        self.spacecraft = Spacecraft("Apollo 11", "NASA", "1969-07-16", hulls=[self.hull1, self.hull2])
        self.classes = {cls.__name__: cls for cls in [Spacecraft, Hull]}

    def test_serialize_primitives(self):
        self.assertEqual(serialize(42), 42)
        self.assertEqual(serialize(3.14), 3.14)
        self.assertEqual(serialize("hello"), "hello")
        self.assertEqual(serialize(True), True)
        self.assertEqual(serialize(None), None)

    def test_serialize_collections(self):
        self.assertEqual(serialize([1, 2, 3]), [1, 2, 3])
        self.assertEqual(serialize({"a": 1, "b": 2}), {"a": 1, "b": 2})
        self.assertEqual(serialize({1, 2, 3}), {"__type__": "set", "items": [1, 2, 3]})
        self.assertEqual(serialize(frozenset([1, 2, 3])), {"__type__": "frozenset", "items": [1, 2, 3]})

    def test_serialize_custom_class(self):
        serialized = serialize(self.spacecraft)
        self.assertIn("__type__", serialized)
        self.assertEqual(serialized["__type__"], "Spacecraft")

    def test_deserialize_primitives(self):
        self.assertEqual(deserialize2(42, self.classes), 42)
        self.assertEqual(deserialize2(3.14, self.classes), 3.14)
        self.assertEqual(deserialize2("hello", self.classes), "hello")
        self.assertEqual(deserialize2(True, self.classes), True)
        self.assertEqual(deserialize2(None, self.classes), None)

    def test_deserialize_collections(self):
        self.assertEqual(deserialize2([1, 2, 3], self.classes), [1, 2, 3])
        self.assertEqual(deserialize2({"a": 1, "b": 2}, self.classes), {"a": 1, "b": 2})
        self.assertEqual(deserialize2({"__type__": "set", "items": [1, 2, 3]}, self.classes), {1, 2, 3})
        self.assertEqual(deserialize2({"__type__": "frozenset", "items": [1, 2, 3]}, self.classes), frozenset([1, 2, 3]))

    def test_deserialize_custom_class(self):
        serialized = serialize(self.spacecraft)
        deserialized = deserialize2(serialized, self.classes)
        self.assertEqual(deserialized.name, self.spacecraft.name)
        self.assertEqual(deserialized.manufacturer, self.spacecraft.manufacturer)
        self.assertEqual(deserialized.launch_date, self.spacecraft.launch_date)
        self.assertEqual(len(deserialized.hulls), len(self.spacecraft.hulls))

    def test_serialize_error(self):
        with self.assertRaises(SerializationError):
            serialize(object())

    def test_deserialize_error(self):
        with self.assertRaises(DeserializationError):
            deserialize2({"__type__": "UnknownClass"}, self.classes)


if __name__ == "__main__":
    unittest.main()
