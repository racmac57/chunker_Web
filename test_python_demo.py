"""
Test Python file for structure analysis
"""

import os
import logging
from typing import List, Dict

class TestClass:
    """A test class with methods."""
    
    def __init__(self):
        """Initialize the test class."""
        self.value = 42
    
    def public_method(self):
        """A public method."""
        return self.value
    
    def _private_method(self):
        """A private method."""
        return "private"

def test_function(param1: str, param2: int = 10) -> str:
    """A test function with parameters."""
    return f"{param1}: {param2}"

CONSTANT_VALUE = "test"

if __name__ == "__main__":
    print("Test")
