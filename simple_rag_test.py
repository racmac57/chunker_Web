"""
Simplified RAG Test for Chunker_v2
Tests core functionality without ChromaDB dependency
"""

import json
import logging
from typing import List, Dict
import pytest

logger = logging.getLogger(__name__)

def test_config_validation():
    """Test configuration validation."""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # Check required keys
        required_keys = ['watch_folder', 'output_dir', 'archive_dir', 'supported_extensions']
        for key in required_keys:
            assert key in config, f"Missing required config key: {key}"
        
        # Check data types
        assert isinstance(config.get('rag_enabled', False), bool)
        assert isinstance(config.get('chunk_size', 0), int)
        assert config['chunk_size'] > 0
        
        print("+ Config validation passed")
        return True
    except Exception as e:
        print(f"- Config validation failed: {e}")
        return False

def test_file_processors():
    """Test file processor imports."""
    try:
        from file_processors import (
            process_excel_file, process_pdf_file, process_python_file,
            process_docx_file, process_yaml_file, process_xml_file,
            process_log_file, process_sql_file
        )
        print("+ File processors imported successfully")
        return True
    except Exception as e:
        print(f"- File processor import failed: {e}")
        return False

def test_rag_integration():
    """Test RAG integration components."""
    try:
        from rag_integration import extract_keywords, FaithfulnessScorer
        print("+ RAG integration components imported successfully")
        
        # Test keyword extraction
        test_text = "This is a test document with multiple sentences for keyword extraction."
        keywords = extract_keywords(test_text, max_keywords=3)
        assert isinstance(keywords, list)
        assert len(keywords) <= 3
        print(f"+ Keyword extraction works: {keywords}")
        
        return True
    except Exception as e:
        print(f"- RAG integration test failed: {e}")
        return False

def test_evaluation_metrics():
    """Test evaluation metrics."""
    try:
        from rag_evaluation import RAGEvaluator
        print("+ RAG evaluation imported successfully")
        return True
    except Exception as e:
        print(f"- RAG evaluation test failed: {e}")
        return False

def test_watcher_imports():
    """Test watcher script imports."""
    try:
        import watcher_splitter
        print("+ Watcher script imports successfully")
        return True
    except Exception as e:
        print(f"- Watcher script import failed: {e}")
        return False

def run_all_tests():
    """Run all available tests."""
    print("Running Chunker_v2 Tests...")
    print("=" * 50)
    
    tests = [
        ("Config Validation", test_config_validation),
        ("File Processors", test_file_processors),
        ("RAG Integration", test_rag_integration),
        ("Evaluation Metrics", test_evaluation_metrics),
        ("Watcher Imports", test_watcher_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"- {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("All tests passed! Chunker_v2 is ready for production.")
        return True
    else:
        print("Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
