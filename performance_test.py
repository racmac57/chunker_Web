#!/usr/bin/env python3
"""
Performance Test Script for Chunker_v2
Tests the speed enhancements for processing large batches of files
"""

import time
import os
import shutil
from pathlib import Path

def create_test_files(count=100, base_dir="02_data"):
    """Create test files for performance testing"""
    print(f"Creating {count} test files...")
    
    # Create base directory
    Path(base_dir).mkdir(exist_ok=True)
    
    # Sample content for different file types
    sample_contents = {
        ".txt": "This is a test file for performance testing. " * 50,
        ".md": "# Test Document\n\nThis is a markdown test file. " * 30,
        ".py": "def test_function():\n    '''Test function'''\n    return 'Hello World'\n" * 20,
        ".json": '{"test": "data", "number": 123, "array": [1, 2, 3]}' * 10
    }
    
    created_files = []
    
    for i in range(count):
        # Alternate between file types
        ext = list(sample_contents.keys())[i % len(sample_contents)]
        filename = f"perf_test_{i:03d}{ext}"
        filepath = Path(base_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sample_contents[ext])
        
        created_files.append(filepath)
    
    print(f"Created {len(created_files)} test files")
    return created_files

def cleanup_test_files(base_dir="02_data"):
    """Clean up test files"""
    print("Cleaning up test files...")
    
    if Path(base_dir).exists():
        for file in Path(base_dir).glob("perf_test_*"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Could not delete {file}: {e}")
    
    # Clean up output directories
    for output_dir in ["04_output", "03_archive", "source"]:
        if Path(output_dir).exists():
            for item in Path(output_dir).glob("*perf_test_*"):
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"Could not delete {item}: {e}")

def run_performance_test():
    """Run a performance test"""
    print("=== Chunker_v2 Performance Test ===")
    print()
    
    # Test with different file counts
    test_counts = [10, 50, 100]
    
    for count in test_counts:
        print(f"\n--- Testing with {count} files ---")
        
        # Clean up first
        cleanup_test_files()
        
        # Create test files
        start_time = time.time()
        test_files = create_test_files(count)
        creation_time = time.time() - start_time
        
        print(f"File creation time: {creation_time:.2f}s")
        print(f"Files ready for processing...")
        print()
        print("Now run: python watcher_splitter.py")
        print("Monitor the logs for processing speed improvements!")
        print()
        print("Expected improvements:")
        print(f"- Parallel processing: Up to {min(8, count)} workers")
        print(f"- Faster stability checks: ~1s instead of 3s per file")
        print(f"- Batch database operations: Reduced locking")
        print(f"- Estimated processing time: ~{count * 0.5:.1f}s instead of {count * 3:.1f}s")
        print()
        
        input("Press Enter to continue to next test...")
        
        # Clean up
        cleanup_test_files()

if __name__ == "__main__":
    run_performance_test()
