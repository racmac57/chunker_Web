#!/usr/bin/env python3
"""
Test script to demonstrate different file filter modes
"""

import json
from pathlib import Path

def test_filter_modes():
    """Test and demonstrate different filter modes"""
    
    # Sample files for testing
    test_files = [
        "document.txt",
        "conversation_full_conversation.txt", 
        "chat_log.txt",
        "meeting_notes.md",
        "important_full_conversation.md",
        "draft_document.txt",
        "temp_file.md",
        "backup_conversation.txt"
    ]
    
    # Test different filter modes
    filter_modes = {
        "all": "Process all files",
        "patterns": "Process files with specific patterns",
        "suffix": "Process only files with _full_conversation suffix"
    }
    
    print("=== File Filter Mode Testing ===\n")
    
    for mode, description in filter_modes.items():
        print(f"Mode: {mode}")
        print(f"Description: {description}")
        print("Files that would be processed:")
        
        if mode == "all":
            # Process all files except those with exclude patterns
            exclude_patterns = ["_draft", "_temp", "_backup"]
            processed = [f for f in test_files if not any(pattern in f for pattern in exclude_patterns)]
            
        elif mode == "patterns":
            # Process files with specific patterns
            file_patterns = ["_full_conversation", "_conversation", "_chat"]
            processed = [f for f in test_files if any(pattern in f for pattern in file_patterns)]
            
        elif mode == "suffix":
            # Process only files with _full_conversation suffix
            processed = [f for f in test_files if "_full_conversation" in f]
        
        for file in processed:
            print(f"  ✓ {file}")
        
        print(f"Total: {len(processed)} files\n")

def show_config_examples():
    """Show configuration examples for different filter modes"""
    
    print("=== Configuration Examples ===\n")
    
    configs = {
        "all": {
            "file_filter_mode": "all",
            "description": "Process all .txt and .md files (except excluded patterns)"
        },
        "patterns": {
            "file_filter_mode": "patterns", 
            "file_patterns": ["_full_conversation", "_conversation", "_chat"],
            "description": "Process files containing any of the specified patterns"
        },
        "suffix": {
            "file_filter_mode": "suffix",
            "description": "Process only files with '_full_conversation' in the name"
        }
    }
    
    for mode, config in configs.items():
        print(f"Mode: {mode}")
        print(f"Description: {config['description']}")
        print("Config:")
        print(json.dumps(config, indent=2))
        print()

def main():
    """Main function"""
    print("File Filter Mode Configuration Guide\n")
    print("The chunker script now supports different file filtering modes:\n")
    
    test_filter_modes()
    show_config_examples()
    
    print("=== How to Configure ===")
    print("1. Edit config.json in the project directory")
    print("2. Set 'file_filter_mode' to one of: 'all', 'patterns', or 'suffix'")
    print("3. For 'patterns' mode, customize 'file_patterns' array")
    print("4. For all modes, customize 'exclude_patterns' array to skip unwanted files")
    print("\nCurrent recommended setting for your use case:")
    print("- Use 'all' mode if you want to process every .txt and .md file")
    print("- Use 'patterns' mode if you want to process only specific file types")
    print("- Use 'suffix' mode if you only want files with '_full_conversation'")

if __name__ == "__main__":
    main()
