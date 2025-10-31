#!/usr/bin/env python3
"""
Test script to verify origin tracking and write-back enhancements.

This script demonstrates the three enhancements:
1. Enhanced sidecar with origin metadata
2. Better front matter with origin info
3. Sidecar copy to source in write-back

Author: R. A. Carucci
Date: 2025-10-30
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def hello_world():
    """Simple hello world function for testing."""
    print("Hello, World!")
    return "Hello from the test script!"


class TestClass:
    """Test class for code block extraction."""

    def __init__(self, name):
        """Initialize with a name."""
        self.name = name

    def greet(self):
        """Return a greeting message."""
        return f"Hello, {self.name}!"

    def process_data(self, data):
        """
        Process some data.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        processed = [x * 2 for x in data]
        return processed


def main():
    """Main test function."""
    print("=== Origin Tracking Test ===")
    print(f"Script: {__file__}")
    print(f"Time: {datetime.now()}")

    # Test the functions
    result = hello_world()
    print(f"Result: {result}")

    # Test the class
    obj = TestClass("Tester")
    greeting = obj.greet()
    print(f"Greeting: {greeting}")

    # Test data processing
    test_data = [1, 2, 3, 4, 5]
    processed = obj.process_data(test_data)
    print(f"Processed data: {processed}")

    print("\n=== Test Complete ===")
    print("This file should be processed with:")
    print("1. Enhanced origin metadata in JSON sidecar")
    print("2. Better front matter in transcript")
    print("3. Sidecar copied to source folder")


if __name__ == "__main__":
    main()
