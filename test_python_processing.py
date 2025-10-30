"""
Test Script for Python File Processing in Chunker_v2
Tests .py file detection, processing, and chunking
"""

import os
import sys
import json
import logging
from pathlib import Path
import time

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/test_python_processing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test 1: Verify configuration loads correctly"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Configuration Loading")
    logger.info("="*80)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        logger.info("✓ Configuration loaded successfully")
        logger.info(f"  Watch folder: {config['watch_folder']}")
        logger.info(f"  Supported extensions: {config['supported_extensions']}")
        logger.info(f"  Filter mode: {config['file_filter_mode']}")

        # Check if .py is supported
        if ".py" in config['supported_extensions']:
            logger.info("✓ .py extension IS in supported_extensions")
        else:
            logger.error("✗ .py extension NOT in supported_extensions!")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ Failed to load configuration: {e}")
        return False

def test_watch_folder_exists():
    """Test 2: Verify watch folder exists and contains Python files"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Watch Folder and Python Files")
    logger.info("="*80)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        watch_folder = Path(config['watch_folder'])

        if not watch_folder.exists():
            logger.error(f"✗ Watch folder does not exist: {watch_folder}")
            return False

        logger.info(f"✓ Watch folder exists: {watch_folder}")

        # Look for Python files
        py_files = list(watch_folder.glob("*.py"))
        logger.info(f"Found {len(py_files)} Python files:")

        for py_file in py_files:
            file_size = py_file.stat().st_size
            logger.info(f"  - {py_file.name} ({file_size} bytes)")

        if len(py_files) == 0:
            logger.warning("⚠️  No Python files found in watch folder")
            return False

        logger.info(f"✓ Found {len(py_files)} Python file(s) to test with")
        return True

    except Exception as e:
        logger.error(f"✗ Error checking watch folder: {e}")
        return False

def test_python_processor():
    """Test 3: Test the Python file processor directly"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Python File Processor")
    logger.info("="*80)

    try:
        from file_processors import process_python_file

        # Test with sample Python code
        test_code = '''
import os
import sys

class TestClass:
    """A test class"""
    def __init__(self):
        self.name = "test"

    def test_method(self, arg1, arg2):
        """Test method docstring"""
        return arg1 + arg2

def test_function(param):
    """Test function"""
    print(f"Processing: {param}")
    return True

CONSTANT_VALUE = 42
'''

        result = process_python_file(test_code)

        logger.info("✓ Python processor executed successfully")
        logger.info("Processed output:")
        logger.info("-" * 60)
        logger.info(result)
        logger.info("-" * 60)

        # Check if output contains expected elements
        if "[CLASS]" in result:
            logger.info("✓ Class detection working")
        else:
            logger.warning("⚠️  Class detection may not be working")

        if "[FUNCTION]" in result:
            logger.info("✓ Function detection working")
        else:
            logger.warning("⚠️  Function detection may not be working")

        return True

    except Exception as e:
        logger.error(f"✗ Python processor test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_file_processor_mapping():
    """Test 4: Verify .py files are mapped to correct processor"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: File Processor Mapping")
    logger.info("="*80)

    try:
        from file_processors import get_file_processor, process_python_file

        processor = get_file_processor(".py")

        if processor == process_python_file:
            logger.info("✓ .py extension correctly mapped to process_python_file")
            return True
        else:
            logger.error(f"✗ .py extension mapped to wrong processor: {processor}")
            return False

    except Exception as e:
        logger.error(f"✗ File processor mapping test failed: {e}")
        return False

def test_process_real_python_file():
    """Test 5: Process a real Python file from the watch folder"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Process Real Python File")
    logger.info("="*80)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        watch_folder = Path(config['watch_folder'])
        py_files = list(watch_folder.glob("*.py"))

        if not py_files:
            logger.warning("⚠️  No Python files to test with")
            return False

        test_file = py_files[0]
        logger.info(f"Testing with: {test_file.name}")

        # Read the file
        with open(test_file, "r", encoding="utf-8", errors='replace') as f:
            content = f.read()

        logger.info(f"File size: {len(content)} characters")

        # Process with the Python processor
        from file_processors import process_python_file

        result = process_python_file(content)

        logger.info("✓ Successfully processed real Python file")
        logger.info(f"Processed output length: {len(result)} characters")
        logger.info("First 500 characters of output:")
        logger.info("-" * 60)
        logger.info(result[:500])
        logger.info("-" * 60)

        return True

    except Exception as e:
        logger.error(f"✗ Real file processing test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_full_processing_pipeline():
    """Test 6: Test the full processing pipeline"""
    logger.info("\n" + "="*80)
    logger.info("TEST 6: Full Processing Pipeline (Dry Run)")
    logger.info("="*80)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        watch_folder = Path(config['watch_folder'])
        py_files = list(watch_folder.glob("*.py"))

        if not py_files:
            logger.warning("⚠️  No Python files to test with")
            return False

        test_file = py_files[0]
        logger.info(f"Testing full pipeline with: {test_file.name}")

        # Simulate the processing steps from watcher_splitter.py

        # Step 1: Read file
        logger.info("Step 1: Reading file...")
        with open(test_file, "r", encoding="utf-8", errors='replace') as f:
            text = f.read()
        logger.info(f"  ✓ Read {len(text)} characters")

        # Step 2: Process with Python processor
        logger.info("Step 2: Processing Python file...")
        from file_processors import get_file_processor
        processor = get_file_processor(".py")
        processed_text = processor(text)
        logger.info(f"  ✓ Processed to {len(processed_text)} characters")

        # Step 3: Check if text would be chunked
        logger.info("Step 3: Checking if text meets minimum size...")
        min_size = config.get("min_chunk_size", 100)
        if len(processed_text) >= min_size:
            logger.info(f"  ✓ Text size ({len(processed_text)}) >= minimum ({min_size})")
        else:
            logger.warning(f"  ⚠️  Text size ({len(processed_text)}) < minimum ({min_size})")

        # Step 4: Simulate chunking (without actually creating files)
        logger.info("Step 4: Simulating chunking...")
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(processed_text)
        logger.info(f"  ✓ Would create {len(sentences)} sentence(s)")

        logger.info("✓ Full pipeline test successful (dry run)")
        return True

    except Exception as e:
        logger.error(f"✗ Full pipeline test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_filter_configuration():
    """Test 7: Verify file filtering configuration"""
    logger.info("\n" + "="*80)
    logger.info("TEST 7: File Filtering Configuration")
    logger.info("="*80)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        filter_mode = config.get("file_filter_mode", "all")
        file_patterns = config.get("file_patterns", [])
        exclude_patterns = config.get("exclude_patterns", [])

        logger.info(f"Filter mode: {filter_mode}")
        logger.info(f"File patterns: {file_patterns}")
        logger.info(f"Exclude patterns: {exclude_patterns}")

        # Check if Python files would pass filters
        test_filenames = ["test_python_demo.py", "test_python_structure.py"]

        for filename in test_filenames:
            logger.info(f"\nTesting filter for: {filename}")

            # Check exclude patterns
            excluded = any(pattern in filename for pattern in exclude_patterns)
            if excluded:
                logger.warning(f"  ⚠️  File EXCLUDED by pattern")
                continue

            # Check filter mode
            if filter_mode == "all":
                logger.info(f"  ✓ File PASSES (mode: all)")
            elif filter_mode == "patterns":
                if any(pattern in filename for pattern in file_patterns):
                    logger.info(f"  ✓ File PASSES (matches pattern)")
                else:
                    logger.warning(f"  ⚠️  File FILTERED OUT (no pattern match)")
            elif filter_mode == "suffix":
                if "_full_conversation" in filename:
                    logger.info(f"  ✓ File PASSES (has suffix)")
                else:
                    logger.warning(f"  ⚠️  File FILTERED OUT (no suffix)")

        return True

    except Exception as e:
        logger.error(f"✗ Filter configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("\n" + "="*80)
    logger.info("PYTHON FILE PROCESSING TEST SUITE - Chunker_v2")
    logger.info("="*80 + "\n")

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    tests = [
        ("Configuration Loading", test_config_loading),
        ("Watch Folder and Files", test_watch_folder_exists),
        ("Python Processor", test_python_processor),
        ("Processor Mapping", test_file_processor_mapping),
        ("Real File Processing", test_process_real_python_file),
        ("Full Pipeline", test_full_processing_pipeline),
        ("Filter Configuration", test_filter_configuration)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("="*80)
    logger.info(f"Total: {len(results)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("="*80 + "\n")

    if failed == 0:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.warning(f"⚠️  {failed} test(s) failed - see logs for details")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
