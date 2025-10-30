"""
LangSmith Integration for Chunker_v2
Provides tracing, evaluation, and feedback collection for RAG pipeline
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from langsmith import Client, traceable
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
import time

logger = logging.getLogger(__name__)

class LangSmithIntegration:
    """
    LangSmith integration for tracing and evaluation.
    """
    
    def __init__(self, api_key: str = None, project: str = "chunker-rag-eval"):
        """
        Initialize LangSmith integration.
        
        Args:
            api_key: LangSmith API key
            project: Project name for tracing
        """
        self.api_key = api_key or os.getenv("LANGCHAIN_API_KEY")
        self.project = project
        
        if not self.api_key:
            logger.warning("LangSmith API key not provided. Tracing will be disabled.")
            self.client = None
        else:
            try:
                os.environ["LANGCHAIN_API_KEY"] = self.api_key
                os.environ["LANGCHAIN_PROJECT"] = self.project
                self.client = Client()
                logger.info(f"Initialized LangSmith client for project: {self.project}")
            except Exception as e:
                logger.error(f"Failed to initialize LangSmith client: {e}")
                self.client = None
    
    @traceable(run_type="chain")
    def traced_rag_query(self, query: str, rag_system, llm=None) -> Dict[str, Any]:
        """
        Traced RAG query with LangSmith tracing.
        
        Args:
            query: Input query
            rag_system: RAG system for retrieval
            llm: Optional LLM for answer generation
            
        Returns:
            Query results with tracing
        """
        try:
            # Retrieve relevant documents
            retrieved_results = rag_system.hybrid_search(query, top_k=5)
            
            # Generate context
            context = "\n".join([r["content"] for r in retrieved_results])
            
            # Generate answer
            if llm:
                answer = llm.invoke(f"Context: {context}\nQuery: {query}")
            else:
                answer = f"Based on the context: {context[:200]}..."
            
            return {
                "query": query,
                "answer": answer,
                "context": context,
                "retrieved_docs": [r["metadata"] for r in retrieved_results],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Traced RAG query failed: {e}")
            return {
                "query": query,
                "answer": "",
                "context": "",
                "retrieved_docs": [],
                "success": False,
                "error": str(e)
            }
    
    def create_feedback(self, run_id: str, score: float, comment: str = "", key: str = "user_feedback") -> bool:
        """
        Create feedback for a run.
        
        Args:
            run_id: LangSmith run ID
            score: Feedback score (0-1)
            comment: Optional comment
            key: Feedback key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("LangSmith client not available")
            return False
        
        try:
            self.client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                comment=comment
            )
            logger.info(f"Created feedback for run {run_id}: {score}")
            return True
        except Exception as e:
            logger.error(f"Failed to create feedback: {e}")
            return False
    
    def evaluate_retrieval(self, run: Run, example: Example) -> Dict[str, float]:
        """
        Evaluate retrieval quality.
        
        Args:
            run: LangSmith run
            example: Example with expected outputs
            
        Returns:
            Retrieval evaluation metrics
        """
        try:
            retrieved_docs = run.outputs.get("retrieved_docs", [])
            expected_sources = example.outputs.get("expected_sources", [])
            
            if not retrieved_docs or not expected_sources:
                return {"precision": 0.0, "recall": 0.0}
            
            # Calculate precision and recall
            retrieved_sources = [doc.get("source_file", "") for doc in retrieved_docs]
            relevant_count = sum(1 for source in retrieved_sources if source in expected_sources)
            
            precision = relevant_count / len(retrieved_sources) if retrieved_sources else 0.0
            recall = relevant_count / len(expected_sources) if expected_sources else 0.0
            
            return {
                "precision": precision,
                "recall": recall,
                "f1": 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Retrieval evaluation failed: {e}")
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    def evaluate_answer_relevance(self, run: Run, example: Example) -> Dict[str, float]:
        """
        Evaluate answer relevance.
        
        Args:
            run: LangSmith run
            example: Example with expected outputs
            
        Returns:
            Answer relevance metrics
        """
        try:
            generated_answer = run.outputs.get("answer", "")
            expected_answer = example.outputs.get("expected_answer", "")
            
            if not generated_answer or not expected_answer:
                return {"relevance": 0.0}
            
            # Simple keyword-based relevance (can be enhanced with embeddings)
            generated_words = set(generated_answer.lower().split())
            expected_words = set(expected_answer.lower().split())
            
            overlap = len(generated_words & expected_words)
            relevance = overlap / len(expected_words) if expected_words else 0.0
            
            return {"relevance": relevance}
            
        except Exception as e:
            logger.error(f"Answer relevance evaluation failed: {e}")
            return {"relevance": 0.0}
    
    def evaluate_context_relevance(self, run: Run, example: Example) -> Dict[str, float]:
        """
        Evaluate context relevance.
        
        Args:
            run: LangSmith run
            example: Example with expected outputs
            
        Returns:
            Context relevance metrics
        """
        try:
            context = run.outputs.get("context", "")
            query = run.inputs.get("query", "")
            
            if not context or not query:
                return {"context_relevance": 0.0}
            
            # Simple keyword-based relevance (can be enhanced with embeddings)
            context_words = set(context.lower().split())
            query_words = set(query.lower().split())
            
            overlap = len(context_words & query_words)
            relevance = overlap / len(query_words) if query_words else 0.0
            
            return {"context_relevance": relevance}
            
        except Exception as e:
            logger.error(f"Context relevance evaluation failed: {e}")
            return {"context_relevance": 0.0}
    
    def run_evaluation(self, examples: List[Example], rag_func: Callable, 
                      experiment_prefix: str = "rag-eval") -> Dict[str, Any]:
        """
        Run evaluation on examples.
        
        Args:
            examples: List of examples to evaluate
            rag_func: RAG function to evaluate
            experiment_prefix: Prefix for experiment name
            
        Returns:
            Evaluation results
        """
        if not self.client:
            logger.warning("LangSmith client not available. Skipping evaluation.")
            return {"error": "LangSmith client not available"}
        
        try:
            # Define evaluators
            evaluators = [
                self.evaluate_retrieval,
                self.evaluate_answer_relevance,
                self.evaluate_context_relevance
            ]
            
            # Run evaluation
            results = evaluate(
                rag_func,
                data=examples,
                evaluators=evaluators,
                experiment_prefix=experiment_prefix
            )
            
            logger.info(f"Evaluation completed: {experiment_prefix}")
            return results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {"error": str(e)}
    
    def load_evaluation_dataset(self, file_path: str) -> List[Example]:
        """
        Load evaluation dataset from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of Example objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            examples = []
            for item in data:
                example = Example(
                    inputs={"query": item["query"]},
                    outputs={
                        "expected_answer": item.get("expected_answer", ""),
                        "expected_sources": item.get("expected_sources", [])
                    }
                )
                examples.append(example)
            
            logger.info(f"Loaded {len(examples)} examples from {file_path}")
            return examples
            
        except Exception as e:
            logger.error(f"Failed to load evaluation dataset: {e}")
            return []
    
    def create_evaluation_dataset(self, test_queries: List[Dict[str, Any]], output_path: str) -> None:
        """
        Create evaluation dataset file.
        
        Args:
            test_queries: List of test queries
            output_path: Output file path
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(test_queries, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created evaluation dataset: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to create evaluation dataset: {e}")
    
    def get_run_traces(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get traces for a specific run.
        
        Args:
            run_id: LangSmith run ID
            
        Returns:
            Run traces or None if failed
        """
        if not self.client:
            logger.warning("LangSmith client not available")
            return None
        
        try:
            run = self.client.read_run(run_id)
            return {
                "run_id": run.id,
                "name": run.name,
                "start_time": run.start_time,
                "end_time": run.end_time,
                "status": run.status,
                "inputs": run.inputs,
                "outputs": run.outputs,
                "error": run.error
            }
        except Exception as e:
            logger.error(f"Failed to get run traces: {e}")
            return None
    
    def get_project_stats(self) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Returns:
            Project statistics
        """
        if not self.client:
            logger.warning("LangSmith client not available")
            return {"error": "LangSmith client not available"}
        
        try:
            # Get project runs
            runs = list(self.client.list_runs(project_name=self.project, limit=100))
            
            stats = {
                "total_runs": len(runs),
                "successful_runs": sum(1 for run in runs if run.status == "success"),
                "failed_runs": sum(1 for run in runs if run.status == "error"),
                "project_name": self.project,
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get project stats: {e}")
            return {"error": str(e)}

def initialize_langsmith(api_key: str = None, project: str = "chunker-rag-eval") -> LangSmithIntegration:
    """
    Initialize LangSmith integration.
    
    Args:
        api_key: LangSmith API key
        project: Project name
        
    Returns:
        LangSmithIntegration instance
    """
    return LangSmithIntegration(api_key=api_key, project=project)

def create_sample_evaluation_dataset() -> List[Dict[str, Any]]:
    """
    Create sample evaluation dataset.
    
    Returns:
        List of sample test queries
    """
    return [
        {
            "query": "How do I fix vlookup errors in Excel?",
            "expected_answer": "Check data types and table references for vlookup errors.",
            "expected_sources": ["excel_guide.md", "troubleshooting.xlsx"],
            "category": "excel"
        },
        {
            "query": "What is Power BI query syntax?",
            "expected_answer": "Power BI uses M language for Power Query transformations.",
            "expected_sources": ["powerbi_guide.md", "m_language_reference.md"],
            "category": "powerbi"
        },
        {
            "query": "How do I use pandas for data analysis?",
            "expected_answer": "Pandas provides data structures and tools for data analysis.",
            "expected_sources": ["python_guide.md", "pandas_tutorial.md"],
            "category": "python"
        }
    ]

# Example usage
if __name__ == "__main__":
    # Initialize LangSmith
    langsmith = initialize_langsmith()
    
    # Create sample dataset
    sample_dataset = create_sample_evaluation_dataset()
    
    # Save dataset
    langsmith.create_evaluation_dataset(sample_dataset, "test_queries.json")
    
    # Load dataset
    examples = langsmith.load_evaluation_dataset("test_queries.json")
    print(f"Loaded {len(examples)} examples")
    
    # Get project stats
    stats = langsmith.get_project_stats()
    print(f"Project stats: {stats}")
    
    print("LangSmith integration test completed successfully!")
