#!/usr/bin/env python3
"""Unit tests for utils module.

This module contains unit tests for the utils module functions.
It tests the access_nested_map function with various input scenarios.
"""
import unittest
from typing import Dict, Tuple, Union, Any
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function.

    This class contains unit tests for the access_nested_map function
    from the utils module to ensure it correctly accesses nested mappings.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Dict[str, Any],
                               path: Tuple[str, ...], expected: Any) -> None:
        """Test that access_nested_map returns expected results."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: Dict[str, Any],
                                         path: Tuple[str, ...],
                                         expected_exception: str) -> None:
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_exception}'")


class TestGetJson(unittest.TestCase):
    """Test class for get_json function.

    This class contains unit tests for the get_json function
    from the utils module to ensure it correctly handles HTTP requests
    and returns JSON data.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: Dict[str, Any],
                      mock_get: Mock) -> None:
        """Test that get_json returns expected result with mocked calls."""
        # Configure the mock to return a mock response with json method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assert the mock was called exactly once with the test URL
        mock_get.assert_called_once_with(test_url)

        # Assert the result equals the test payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator.

    This class contains unit tests for the memoize decorator
    from the utils module to ensure it correctly caches method results.
    """

    def test_memoize(self) -> None:
        """Test that memoize decorator correctly caches method results."""

        class TestClass:
            """Test class for memoize decorator testing."""

            def a_method(self):
                """A method that returns a value."""
                return 42

            @memoize
            def a_property(self):
                """A memoized property that calls a_method."""
                return self.a_method()

        # Create an instance of the test class
        test_instance = TestClass()

        # Patch the a_method to track calls
        with patch.object(test_instance, 'a_method',
                          return_value=42) as mock_method:
            # Call a_property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assert both calls return the correct result
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Assert a_method was only called once
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
