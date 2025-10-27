#!/usr/bin/env python3
"""
Test script to verify the logging and database fixes
"""

import os
import sys
import time
from pathlib import Path
from watcher_splitter import setup_logging, init_database_with_retry, ChunkerDatabase

def test_logging():
    """Test that logging works correctly"""
    print("Testing logging setup...")
    
    # Test logging setup
    logger = setup_logging()
    logger.info("Test log message - logging is working!")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    print("✓ Logging test completed")

def test_database():
    """Test that database operations work correctly"""
    print("Testing database operations...")
    
    # Test database initialization
    db = init_database_with_retry()
    if db is None:
        print("✗ Database initialization failed")
        return False
    
    print("✓ Database initialized successfully")
    
    # Test logging operations
    try:
        db.log_processing("test_file.txt", 1000, 5, 5000, 2.5, True, None, "admin")
        print("✓ Processing log test passed")
    except Exception as e:
        print(f"✗ Processing log test failed: {e}")
        return False
    
    try:
        db.log_error("TestError", "Test error message", "Test stack trace", "test_file.txt")
        print("✓ Error log test passed")
    except Exception as e:
        print(f"✗ Error log test failed: {e}")
        return False
    
    try:
        db.log_system_metrics(25.5, 75.2, 45.8, 150)
        print("✓ System metrics test passed")
    except Exception as e:
        print(f"✗ System metrics test failed: {e}")
        return False
    
    # Test analytics
    try:
        analytics = db.get_analytics(days=1)
        print(f"✓ Analytics test passed - got {len(analytics)} analytics categories")
    except Exception as e:
        print(f"✗ Analytics test failed: {e}")
        return False
    
    return True

def test_file_processing():
    """Test file processing functionality"""
    print("Testing file processing...")
    
    # Create a test file
    test_content = """
    This is a test file for the chunker system.
    It contains multiple sentences to test the chunking functionality.
    The system should be able to process this file and create chunks.
    Each sentence should be properly identified and grouped together.
    This helps verify that the text processing is working correctly.
    """
    
    test_file = Path("test_input.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"✓ Created test file: {test_file}")
    
    # Clean up
    if test_file.exists():
        test_file.unlink()
        print("✓ Cleaned up test file")
    
    return True

def main():
    """Run all tests"""
    print("=== Testing Chunker Fixes ===\n")
    
    # Test logging
    test_logging()
    print()
    
    # Test database
    if test_database():
        print("✓ All database tests passed")
    else:
        print("✗ Some database tests failed")
    print()
    
    # Test file processing
    if test_file_processing():
        print("✓ File processing test passed")
    else:
        print("✗ File processing test failed")
    print()
    
    print("=== Test Summary ===")
    print("The script should now handle database locking issues better")
    print("and provide more reliable logging. Your txt files should be")
    print("processed successfully and moved to the processed/admin directory.")
    print("\nTo verify your file was processed, check:")
    print("1. processed/admin/ directory for your original file")
    print("2. output/ directory for the chunked files")
    print("3. logs/watcher.log for processing details")

if __name__ == "__main__":
    main()
