"""
RAG Testing Script for Chunker_v2
Automated testing of RAG evaluation pipeline
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Import RAG components
try:
    from rag_integration import ChromaRAG, FaithfulnessScorer
    from rag_evaluation import RAGEvaluator, run_evaluation_pipeline
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG components not available: {e}")
    RAG_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_test_queries(test_file: str = "test_queries.json") -> List[Dict[str, Any]]:
    """
    Load test queries from JSON file
    
    Args:
        test_file: Path to test queries file
        
    Returns:
        List of test query dictionaries
    """
    try:
        with open(test_file, 'r') as f:
            queries = json.load(f)
        logger.info(f"Loaded {len(queries)} test queries from {test_file}")
        return queries
    except FileNotFoundError:
        logger.error(f"Test queries file not found: {test_file}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test queries file: {e}")
        return []


def setup_test_rag_system() -> ChromaRAG:
    """
    Setup RAG system for testing
    
    Returns:
        ChromaRAG instance
    """
    try:
        rag = ChromaRAG(persist_directory="./test_chroma_db")
        
        # Add some test documents
        test_docs = [
            "VLOOKUP is used to find values in a table. Syntax: VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])",
            "Power BI uses M language for Power Query. You can create custom functions and data transformations.",
            "Python files can be processed using AST module to extract functions, classes, and imports.",
            "Chunking parameters include chunk size, overlap, and sentence limits for text processing.",
            "Database tracking uses SQLite to store processing metrics, errors, and system performance data."
        ]
        
        for i, doc in enumerate(test_docs):
            metadata = {
                "file_name": f"test_doc_{i+1}.md",
                "file_type": ".md",
                "chunk_index": 1,
                "timestamp": "2025-10-27T12:00:00Z",
                "department": "admin",
                "keywords": ["test", "document"],
                "file_size": len(doc),
                "processing_time": 0.1
            }
            rag.add_chunk(doc, metadata)
        
        logger.info("Test RAG system setup complete")
        return rag
        
    except Exception as e:
        logger.error(f"Failed to setup test RAG system: {e}")
        return None


def run_rag_tests() -> Dict[str, Any]:
    """
    Run comprehensive RAG tests
    
    Returns:
        Test results dictionary
    """
    if not RAG_AVAILABLE:
        return {"error": "RAG components not available"}
    
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "test_results": [],
        "overall_score": 0.0
    }
    
    try:
        # Setup test system
        rag_system = setup_test_rag_system()
        if not rag_system:
            results["error"] = "Failed to setup test RAG system"
            return results
        
        # Load test queries
        test_queries = load_test_queries()
        if not test_queries:
            results["error"] = "No test queries available"
            return results
        
        # Initialize evaluators
        faithfulness_scorer = FaithfulnessScorer()
        evaluator = RAGEvaluator()
        
        # Run evaluation pipeline
        evaluation_results = run_evaluation_pipeline(
            test_queries, rag_system, faithfulness_scorer
        )
        
        # Analyze results
        total_score = 0.0
        valid_tests = 0
        
        for result in evaluation_results:
            if "error" in result:
                results["tests_failed"] += 1
                results["test_results"].append({
                    "query": result.get("query", "Unknown"),
                    "status": "failed",
                    "error": result["error"]
                })
                continue
            
            # Check retrieval metrics
            retrieval_metrics = result.get("retrieval_metrics", {})
            precision_at_k = retrieval_metrics.get("precision_at_k", 0.0)
            recall_at_k = retrieval_metrics.get("recall_at_k", 0.0)
            mrr = retrieval_metrics.get("mrr", 0.0)
            
            # Check quality metrics
            quality_metrics = result.get("quality_metrics", {})
            faithfulness = result.get("faithfulness", 0.0)
            
            # Calculate test score
            test_score = (precision_at_k + recall_at_k + mrr + faithfulness) / 4.0
            total_score += test_score
            valid_tests += 1
            
            # Determine pass/fail
            passed = test_score >= 0.5  # Threshold for passing
            
            if passed:
                results["tests_passed"] += 1
                status = "passed"
            else:
                results["tests_failed"] += 1
                status = "failed"
            
            results["test_results"].append({
                "query": result["query"],
                "status": status,
                "score": test_score,
                "precision_at_k": precision_at_k,
                "recall_at_k": recall_at_k,
                "mrr": mrr,
                "faithfulness": faithfulness
            })
        
        # Calculate overall score
        if valid_tests > 0:
            results["overall_score"] = total_score / valid_tests
        
        logger.info(f"RAG tests completed: {results['tests_passed']} passed, {results['tests_failed']} failed")
        logger.info(f"Overall score: {results['overall_score']:.3f}")
        
    except Exception as e:
        logger.error(f"RAG tests failed: {e}")
        results["error"] = str(e)
    
    return results


def assert_test_thresholds(results: Dict[str, Any], thresholds: Dict[str, float]) -> bool:
    """
    Assert that test results meet minimum thresholds
    
    Args:
        results: Test results dictionary
        thresholds: Minimum threshold values
        
    Returns:
        True if all thresholds met, False otherwise
    """
    if "error" in results:
        logger.error(f"Tests failed with error: {results['error']}")
        return False
    
    # Check overall score threshold
    overall_threshold = thresholds.get("overall_score", 0.5)
    if results["overall_score"] < overall_threshold:
        logger.error(f"Overall score {results['overall_score']:.3f} below threshold {overall_threshold}")
        return False
    
    # Check individual test thresholds
    precision_threshold = thresholds.get("precision_at_k", 0.3)
    recall_threshold = thresholds.get("recall_at_k", 0.3)
    faithfulness_threshold = thresholds.get("faithfulness", 0.4)
    
    failed_tests = []
    for test_result in results["test_results"]:
        if test_result["status"] == "failed":
            continue
        
        if test_result.get("precision_at_k", 0) < precision_threshold:
            failed_tests.append(f"Precision@K too low for query: {test_result['query']}")
        
        if test_result.get("recall_at_k", 0) < recall_threshold:
            failed_tests.append(f"Recall@K too low for query: {test_result['query']}")
        
        if test_result.get("faithfulness", 0) < faithfulness_threshold:
            failed_tests.append(f"Faithfulness too low for query: {test_result['query']}")
    
    if failed_tests:
        for failure in failed_tests:
            logger.error(failure)
        return False
    
    logger.info("All test thresholds met!")
    return True


def main():
    """Main testing function"""
    print("=== RAG Testing Script ===")
    
    if not RAG_AVAILABLE:
        print("❌ RAG components not available. Please install dependencies.")
        sys.exit(1)
    
    # Define test thresholds
    thresholds = {
        "overall_score": 0.5,
        "precision_at_k": 0.3,
        "recall_at_k": 0.3,
        "faithfulness": 0.4
    }
    
    print(f"Running RAG tests with thresholds: {thresholds}")
    
    # Run tests
    results = run_rag_tests()
    
    # Print results
    print("\n=== Test Results ===")
    if "error" in results:
        print(f"❌ Tests failed: {results['error']}")
        sys.exit(1)
    
    print(f"Tests passed: {results['tests_passed']}")
    print(f"Tests failed: {results['tests_failed']}")
    print(f"Overall score: {results['overall_score']:.3f}")
    
    print("\n=== Individual Test Results ===")
    for test_result in results["test_results"]:
        status_icon = "✅" if test_result["status"] == "passed" else "❌"
        print(f"{status_icon} {test_result['query']}")
        print(f"   Score: {test_result.get('score', 0):.3f}")
        print(f"   Precision@K: {test_result.get('precision_at_k', 0):.3f}")
        print(f"   Recall@K: {test_result.get('recall_at_k', 0):.3f}")
        print(f"   Faithfulness: {test_result.get('faithfulness', 0):.3f}")
        print()
    
    # Assert thresholds
    if assert_test_thresholds(results, thresholds):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed thresholds")
        sys.exit(1)


if __name__ == "__main__":
    main()
