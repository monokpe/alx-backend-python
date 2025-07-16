import unittest
from utils import access_nested_map
from parameterized import parameterized


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for access_nested_map function using parameterized."""
    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
            ({"a": {"b": {"c": 1}}}, ("a", "b", "c"), 1),
            ({"x": {"y": {"z" : {"data": "hello"}}}}, ("x","y", "z", "data"), "hello"),
            # Test case for empty path
            ({"a": 1, "b": 2}, (), {"a": 1, "b": 2}),
        ]
    )
    def test_access_nested_map(self, nested_map, path, expected_value):
         """
        Test that access_nested_map returns the correct value for various inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_value)

    def test_access_nested_map_missing_key(self):
        with self.assertRaises(KeyError):
            access_nested_map({"a": {"b": {}}}, ("a", "b", "c"))

    def test_access_nested_map_empty(self):
        with self.assertRaises(KeyError):
            access_nested_map({}, ("a", "b"))
