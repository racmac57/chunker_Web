#!/usr/bin/env python3
"""
Standalone test script to verify processing workflow with enhanced archive function
Tests the complete move-optimized workflow without requiring Celery or watcher_splitter
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/test_processing.log')
    ]
)
logger = logging.getLogger(__name__)

def test_processing_workflow():
    """
    Test the complete processing workflow including archive MOVE
    """
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        logger.info("="*80)
        logger.info("PROCESSING WORKFLOW TEST")
        logger.info("="*80)
        
        # Check for test file in 02_data
        test_file = Path('02_data/test_move_workflow.md')
        
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            logger.info("Expected file: 02_data/test_move_workflow.md")
            return False
        
        logger.info(f"Found test file: {test_file.name}")
        logger.info(f"File size: {test_file.stat().st_size} bytes")
        
        # Import processing function from celery_tasks
        from celery_tasks import process_file_with_rag
        
        # Process the file
        logger.info("\n" + "="*80)
        logger.info("PROCESSING FILE...")
        logger.info("="*80)
        
        result = process_file_with_rag(
            str(test_file),
            None,  # dest_path
            "created",  # event_type
            config
        )
        
        # Check results
        logger.info("\n" + "="*80)
        logger.info("RESULTS")
        logger.info("="*80)
        
        if result.get('status') == 'success':
            logger.info("✅ Processing successful!")
            logger.info(f"Chunks created: {result.get('chunks_created', 0)}")
            logger.info(f"Output files: {len(result.get('output_files', []))}")
            logger.info(f"Archive result: {result.get('archive_result', 'N/A')}")
            
            # Verify outputs
            output_files = result.get('output_files', [])
            for out_file in output_files:
                if Path(out_file).exists():
                    logger.info(f"✅ Output exists: {out_file}")
                else:
                    logger.error(f"❌ Output missing: {out_file}")
            
            # Verify archive
            archive_path = result.get('archive_result', '')
            if archive_path and Path(archive_path).exists():
                logger.info(f"✅ Archived: {Path(archive_path).name}")
                
                # Check if manifest exists
                manifest_path = Path(archive_path).with_name(f"{Path(archive_path).name}.origin.json")
                if manifest_path.exists():
                    logger.info(f"✅ Manifest attached: {manifest_path.name}")
                else:
                    logger.warning(f"⚠️ Manifest missing: {manifest_path.name}")
            else:
                logger.error("❌ Archive not found!")
            
            # Verify source file removed
            if not test_file.exists():
                logger.info("✅ Source file removed from 02_data")
            else:
                logger.warning("⚠️ Source file still in 02_data")
            
            return True
        else:
            logger.error(f"❌ Processing failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting processing workflow test...")
    success = test_processing_workflow()
    
    if success:
        logger.info("\n" + "="*80)
        logger.info("✅ TEST PASSED")
        logger.info("="*80)
        sys.exit(0)
    else:
        logger.error("\n" + "="*80)
        logger.error("❌ TEST FAILED")
        logger.error("="*80)
        sys.exit(1)










