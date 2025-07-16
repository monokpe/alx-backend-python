#!/usr/bin/env python3
"""Unit tests for utils module."""

import unittest
from typing import Any, Dict, Sequence

from parameterized import parameterized
from unittest.mock import patch

from utils import access_nested_map, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for access_nested_map function using parameterized."""

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(
        self, nested_map: Dict[str, Any], path: Sequence[str], expected: Any
    ) -> None:
        """Test that access_nested_map returns the correct value for various inputs."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand(
        [
            ({}, ("a",)),
            ({"a": 1}, ("a", "b")),
        ]
    )
    def test_access_nested_map_exception(
        self, nested_map: Dict[str, Any], path: Sequence[str]
    ) -> None:
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestMemoize(unittest.TestCase):
    """Unit tests for memoize decorator."""

    def test_memoize(self) -> None:
        """
        Test that memoize caches the result of a function.
        This test checks that the memoized function is only called once.
        """

        class TestClass:
            def a_method(self) -> int:
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, "a_method") as mock_a_method:
            mock_a_method.return_value = 42
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_a_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
