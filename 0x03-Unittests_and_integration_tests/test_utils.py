#!/usr/bin/env python3
"""Unit tests for utils module.

This module contains unit tests for the utils module functions.
It tests the access_nested_map function with various input scenarios.
"""
import unittest
from typing import Dict, Tuple, Union, Any
from parameterized import parameterized
from utils import access_nested_map


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
    def test_access_nested_map(self, nested_map: Dict[str, Any], path: Tuple[str, ...], expected: Any) -> None:
        """Test that access_nested_map returns expected results for given inputs.
        
        This method tests the access_nested_map function with various
        nested dictionary structures and key paths to ensure it returns
        the correct values.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == "__main__":
    unittest.main()
