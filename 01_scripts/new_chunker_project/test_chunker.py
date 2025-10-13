#!/usr/bin/env python3
"""
Test script for the chunker functionality
"""

import os
import sys
from pathlib import Path
from watcher_splitter import chunk_text_enhanced, validate_chunk_content_enhanced, get_department_config

def test_chunking():
    """Test the chunking functionality"""
    print("Testing chunker functionality...")
    
    # Test text
    test_text = """
    This is a test conversation file to verify the chunking functionality. The system should process this file and create chunks based on the configured settings. 
    
    The chunker will split this text into smaller, manageable pieces while maintaining the semantic meaning of the content. Each chunk will be saved as a separate file in the output directory.
    
    This enterprise-grade chunking system includes features like database tracking, parallel processing, and department-specific configurations. It can handle various types of content and apply different rules based on the department or content type.
    
    The system monitors a specific folder for new files and automatically processes them when they are detected. It includes error handling, logging, and notification capabilities to ensure reliable operation in production environments.
    
    Testing the chunking functionality is important to ensure that the system works correctly with different types of content and file sizes. This test file will help verify that the chunking algorithm properly splits text while maintaining readability and context.
    
    The system also includes features like redaction for sensitive content, cloud synchronization, and comprehensive analytics tracking. These features make it suitable for enterprise environments where data security and compliance are important considerations.
    
    Each chunk created by the system will be validated to ensure it meets quality standards and contains meaningful content. The system prevents creation of empty or invalid chunks that could cause issues downstream.
    
    The chunking process is optimized for performance and can handle large files efficiently. The parallel processing capability allows multiple files to be processed simultaneously, improving overall throughput.
    
    This test file should be processed successfully by the chunker system, resulting in multiple output files that can be used for further analysis or processing. The system will log all activities and provide detailed statistics about the processing results.
    """
    
    # Test file path
    test_file = Path("test_conversation_full_conversation.txt")
    
    # Get department config
    dept_config = get_department_config(test_file)
    print(f"Department config: {dept_config.get('department', 'default')}")
    
    # Test chunking
    chunks = chunk_text_enhanced(test_text, 100, dept_config)
    
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks, 1):
        is_valid = validate_chunk_content_enhanced(chunk, department_config=dept_config)
        print(f"  Chunk {i}: {len(chunk)} chars, Valid: {is_valid}")
        if is_valid:
            print(f"    Preview: {chunk[:100]}...")
        print()
    
    # Test with a real file
    if test_file.exists():
        print(f"Testing with real file: {test_file}")
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                file_text = f.read()
            
            file_chunks = chunk_text_enhanced(file_text, 100, dept_config)
            print(f"File processing: Created {len(file_chunks)} chunks")
            
            # Save test chunks
            os.makedirs("output", exist_ok=True)
            for i, chunk in enumerate(file_chunks, 1):
                if validate_chunk_content_enhanced(chunk, department_config=dept_config):
                    output_file = Path("output") / f"test_chunk_{i}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(chunk)
                    print(f"  Saved: {output_file}")
            
        except Exception as e:
            print(f"Error processing file: {e}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_chunking()
