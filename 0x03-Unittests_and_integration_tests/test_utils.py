#!/usr/bin/env python3
"""Unit tests for utils module."""

import unittest
from typing import Any, Dict, Sequence, Tuple, Union

from parameterized import parameterized

from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for access_nested_map function using parameterized."""

    @parameterized.expand(
        [
            # Test case 1: Single level access
            ({"a": 1}, ("a",), 1),
            # Test case 2: Accessing a dictionary at an intermediate level
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            # Test case 3: Accessing a value at a deeper level
            ({"a": {"b": 2}}, ("a", "b"), 2),
            # Test case 4: Deeply nested access
            ({"a": {"b": {"c": 1}}}, ("a", "b", "c"), 1),
            # Test case 5: Another deeply nested access with string data
            ({"x": {"y": {"z": {"data": "hello"}}}}, ("x", "y", "z", "data"), "hello"),
            # Test case 6: Empty path, should return the original map
            ({"a": 1, "b": 2}, (), {"a": 1, "b": 2}),
            # Test case 7: Empty map, empty path
            ({}, (), {}),
        ]
    )
    def test_access_nested_map(
        self, nested_map: Dict[str, Any], path: Sequence[str], expected_value: Any
    ) -> None:
        """
        Test that access_nested_map returns the correct value for various inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_value)

    @parameterized.expand(
        [
            # Test case 1: Key not found at a deeper level
            ({"a": {"b": {"c": 1}}}, ("a", "d")),
            # Test case 2: Key not found at the first level
            ({"a": {"b": {"c": 1}}}, ("x", "y")),
            # Test case 3: Empty map, non-empty path
            ({}, ("a", "b")),
        ]
    )
    def test_access_nested_map_key_not_found(
        self, nested_map: Dict[str, Any], path: Sequence[str]
    ) -> None:
        """
        Test that access_nested_map raises a KeyError when a key in the path does not exist.
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)

    @parameterized.expand(
        [
            # Test case 1: Value at intermediate level is not a map (string)
            ({"a": {"b": "not_a_map"}}, ("a", "b", "c")),
            # Test case 2: Value at intermediate level is an integer
            ({"a": 123}, ("a", "b")),
            # Test case 3: Value at intermediate level is a list
            ({"list_data": [1, 2, 3]}, ("list_data", 0)),
        ]
    )
    def test_access_nested_map_value_not_map_type_error(
        self, nested_map: Dict[str, Any], path: Sequence[Union[str, int]]
    ) -> None:
        """
        Test that access_nested_map raises a KeyError when trying to access a key
        on a value that is not a dictionary (Mapping).
        """
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


if __name__ == "__main__":
    unittest.main()
