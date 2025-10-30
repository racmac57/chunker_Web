"""
Comprehensive RAG Evaluation Framework for Chunker_v2
Advanced metrics, automated testing, and performance monitoring
"""

import os
import json
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class ComprehensiveRAGEvaluator:
    """
    Comprehensive RAG evaluation system with advanced metrics and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize comprehensive RAG evaluator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.evaluation_dir = config.get("evaluation_dir", "./evaluations")
        self.reports_dir = config.get("reports_dir", "./reports")
        self.baseline_file = config.get("baseline_file", "./baseline_metrics.json")
        self.thresholds = config.get("evaluation_thresholds", {})
        
        # Create directories
        os.makedirs(self.evaluation_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Load baseline metrics
        self.baseline_metrics = self._load_baseline_metrics()
        
        # Initialize evaluation components
        self._initialize_evaluation_components()
        
        logger.info("Initialized ComprehensiveRAGEvaluator")
    
    def _initialize_evaluation_components(self) -> None:
        """Initialize evaluation components and models."""
        try:
            # Initialize sentence transformer for semantic similarity
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ROUGE scorer
            from rouge_score import rouge_scorer
            self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            
            # Initialize NLTK components
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            logger.info("Evaluation components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize evaluation components: {e}")
            raise
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline metrics for comparison."""
        try:
            if os.path.exists(self.baseline_file):
                with open(self.baseline_file, 'r') as f:
                    baseline = json.load(f)
                logger.info("Loaded baseline metrics")
                return baseline
            else:
                logger.info("No baseline metrics found")
                return {}
        except Exception as e:
            logger.error(f"Failed to load baseline metrics: {e}")
            return {}
    
    def evaluate_retrieval_metrics(self, retrieved_docs: List[str], relevant_docs: List[str], 
                                 k_values: List[int] = [1, 3, 5, 10]) -> Dict[str, float]:
        """
        Evaluate retrieval performance with comprehensive metrics.
        
        Args:
            retrieved_docs: List of retrieved document IDs
            relevant_docs: List of relevant document IDs
            k_values: List of k values to evaluate
            
        Returns:
            Dictionary of retrieval metrics
        """
        metrics = {}
        
        for k in k_values:
            # Precision@K
            metrics[f"precision_at_{k}"] = self._precision_at_k(retrieved_docs, relevant_docs, k)
            
            # Recall@K
            metrics[f"recall_at_{k}"] = self._recall_at_k(retrieved_docs, relevant_docs, k)
            
            # F1@K
            precision = metrics[f"precision_at_{k}"]
            recall = metrics[f"recall_at_{k}"]
            if precision + recall > 0:
                metrics[f"f1_at_{k}"] = 2 * precision * recall / (precision + recall)
            else:
                metrics[f"f1_at_{k}"] = 0.0
            
            # NDCG@K
            metrics[f"ndcg_at_{k}"] = self._ndcg_at_k(retrieved_docs, relevant_docs, k)
        
        # MRR (Mean Reciprocal Rank)
        metrics["mrr"] = self._mean_reciprocal_rank(retrieved_docs, relevant_docs)
        
        # MAP (Mean Average Precision)
        metrics["map"] = self._mean_average_precision(retrieved_docs, relevant_docs)
        
        return metrics
    
    def evaluate_generation_metrics(self, reference: str, generated: str) -> Dict[str, float]:
        """
        Evaluate generation quality with multiple metrics.
        
        Args:
            reference: Reference answer
            generated: Generated answer
            
        Returns:
            Dictionary of generation metrics
        """
        metrics = {}
        
        # ROUGE scores
        rouge_scores = self.rouge_scorer.score(reference, generated)
        metrics["rouge1"] = rouge_scores["rouge1"].fmeasure
        metrics["rouge2"] = rouge_scores["rouge2"].fmeasure
        metrics["rougeL"] = rouge_scores["rougeL"].fmeasure
        
        # BLEU score
        try:
            from nltk.translate.bleu_score import sentence_bleu
            bleu_score = sentence_bleu([reference.split()], generated.split())
            metrics["bleu"] = bleu_score
        except Exception as e:
            logger.warning(f"BLEU calculation failed: {e}")
            metrics["bleu"] = 0.0
        
        # BERTScore
        try:
            from bert_score import score as bertscore
            P, R, F1 = bertscore([generated], [reference], lang="en")
            metrics["bertscore_precision"] = P.mean().item()
            metrics["bertscore_recall"] = R.mean().item()
            metrics["bertscore_f1"] = F1.mean().item()
        except Exception as e:
            logger.warning(f"BERTScore calculation failed: {e}")
            metrics["bertscore_precision"] = 0.0
            metrics["bertscore_recall"] = 0.0
            metrics["bertscore_f1"] = 0.0
        
        # Semantic similarity
        metrics["semantic_similarity"] = self._calculate_semantic_similarity(reference, generated)
        
        return metrics
    
    def evaluate_faithfulness(self, answer: str, context: str, 
                           threshold: float = 0.7) -> Dict[str, Any]:
        """
        Evaluate faithfulness with detailed analysis.
        
        Args:
            answer: Generated answer
            context: Source context
            threshold: Similarity threshold for claim support
            
        Returns:
            Detailed faithfulness analysis
        """
        try:
            # Extract claims from answer
            claims = self._extract_claims(answer)
            
            if not claims:
                return {
                    "faithfulness_score": 1.0,
                    "total_claims": 0,
                    "supported_claims": 0,
                    "unsupported_claims": 0,
                    "claim_details": []
                }
            
            # Calculate similarity for each claim
            claim_embeddings = self.sentence_model.encode(claims)
            context_embeddings = self.sentence_model.encode([context])
            
            faithfulness_scores = []
            claim_details = []
            
            for i, claim in enumerate(claims):
                similarity = self._cosine_similarity(
                    claim_embeddings[i], 
                    context_embeddings[0]
                )
                
                is_supported = similarity >= threshold
                faithfulness_scores.append(1.0 if is_supported else similarity)
                
                claim_details.append({
                    "claim": claim,
                    "similarity": float(similarity),
                    "supported": is_supported
                })
            
            supported_claims = sum(1 for detail in claim_details if detail["supported"])
            
            return {
                "faithfulness_score": float(np.mean(faithfulness_scores)),
                "total_claims": len(claims),
                "supported_claims": supported_claims,
                "unsupported_claims": len(claims) - supported_claims,
                "claim_details": claim_details
            }
            
        except Exception as e:
            logger.error(f"Faithfulness evaluation failed: {e}")
            return {"faithfulness_score": 0.0, "error": str(e)}
    
    def evaluate_context_utilization(self, answer: str, context: str) -> Dict[str, float]:
        """
        Evaluate how much of the context is utilized in the answer.
        
        Args:
            answer: Generated answer
            context: Source context
            
        Returns:
            Context utilization metrics
        """
        try:
            # Split into sentences
            answer_sentences = self._split_into_sentences(answer)
            context_sentences = self._split_into_sentences(context)
            
            if not answer_sentences or not context_sentences:
                return {"context_utilization": 0.0, "sentence_coverage": 0.0}
            
            # Calculate sentence-level similarities
            answer_embeddings = self.sentence_model.encode(answer_sentences)
            context_embeddings = self.sentence_model.encode(context_sentences)
            
            similarities = self._cosine_similarity_matrix(answer_embeddings, context_embeddings)
            
            # Find best matching context sentence for each answer sentence
            max_similarities = np.max(similarities, axis=1)
            
            # Calculate utilization metrics
            context_utilization = float(np.mean(max_similarities))
            sentence_coverage = float(np.mean(max_similarities >= 0.7))
            
            return {
                "context_utilization": context_utilization,
                "sentence_coverage": sentence_coverage,
                "avg_sentence_similarity": float(np.mean(max_similarities)),
                "max_sentence_similarity": float(np.max(max_similarities))
            }
            
        except Exception as e:
            logger.error(f"Context utilization evaluation failed: {e}")
            return {"context_utilization": 0.0, "sentence_coverage": 0.0, "error": str(e)}
    
    def evaluate_end_to_end(self, query: str, answer: str, context: str,
                          retrieved_docs: List[str] = None, 
                          relevant_docs: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive end-to-end evaluation.
        
        Args:
            query: Input query
            answer: Generated answer
            context: Retrieved context
            retrieved_docs: List of retrieved document IDs
            relevant_docs: List of relevant document IDs
            
        Returns:
            Comprehensive evaluation results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer": answer,
            "context": context
        }
        
        # Generation metrics
        generation_metrics = self.evaluate_generation_metrics(answer, answer)  # Self-reference for now
        results.update(generation_metrics)
        
        # Faithfulness evaluation
        faithfulness_results = self.evaluate_faithfulness(answer, context)
        results.update(faithfulness_results)
        
        # Context utilization
        utilization_results = self.evaluate_context_utilization(answer, context)
        results.update(utilization_results)
        
        # Retrieval metrics (if provided)
        if retrieved_docs and relevant_docs:
            retrieval_metrics = self.evaluate_retrieval_metrics(retrieved_docs, relevant_docs)
            results.update(retrieval_metrics)
        
        # Overall quality score
        results["overall_quality_score"] = self._calculate_overall_quality_score(results)
        
        return results
    
    def run_comprehensive_evaluation(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run comprehensive evaluation on multiple test cases.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Comprehensive evaluation results
        """
        results = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "total_test_cases": len(test_cases),
            "individual_results": [],
            "aggregate_metrics": {},
            "summary": {}
        }
        
        all_metrics = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # Run end-to-end evaluation
                case_result = self.evaluate_end_to_end(
                    test_case.get("query", ""),
                    test_case.get("answer", ""),
                    test_case.get("context", ""),
                    test_case.get("retrieved_docs", []),
                    test_case.get("relevant_docs", [])
                )
                
                case_result["test_case_id"] = i
                case_result["test_case_name"] = test_case.get("name", f"test_case_{i}")
                
                results["individual_results"].append(case_result)
                all_metrics.append(case_result)
                
            except Exception as e:
                logger.error(f"Evaluation failed for test case {i}: {e}")
                results["individual_results"].append({
                    "test_case_id": i,
                    "test_case_name": test_case.get("name", f"test_case_{i}"),
                    "error": str(e),
                    "success": False
                })
        
        # Calculate aggregate metrics
        if all_metrics:
            numeric_keys = [k for k in all_metrics[0].keys() 
                          if isinstance(all_metrics[0][k], (int, float)) and k not in ["test_case_id"]]
            
            for key in numeric_keys:
                values = [m[key] for m in all_metrics if key in m and isinstance(m[key], (int, float))]
                if values:
                    results["aggregate_metrics"][key] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "median": float(np.median(values)),
                        "count": len(values)
                    }
        
        # Generate summary
        results["summary"] = self._generate_evaluation_summary(results["aggregate_metrics"])
        
        # Check for regressions
        regression_alerts = self._check_regressions(results["aggregate_metrics"])
        results["regression_alerts"] = regression_alerts
        
        return results
    
    def _precision_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate Precision@K."""
        if not retrieved or k == 0:
            return 0.0
        
        top_k = retrieved[:k]
        relevant_count = sum(1 for doc in top_k if doc in relevant)
        return relevant_count / k
    
    def _recall_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate Recall@K."""
        if not relevant:
            return 0.0
        
        top_k = retrieved[:k]
        relevant_count = sum(1 for doc in top_k if doc in relevant)
        return relevant_count / len(relevant)
    
    def _ndcg_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calculate NDCG@K."""
        def dcg_at_k(relevance_scores: List[float], k: int) -> float:
            relevance_scores = relevance_scores[:k]
            return sum(score / np.log2(i + 2) for i, score in enumerate(relevance_scores))
        
        # Calculate relevance scores
        relevance_scores = [1.0 if doc in relevant else 0.0 for doc in retrieved]
        
        # Calculate DCG
        dcg = dcg_at_k(relevance_scores, k)
        
        # Calculate IDCG
        ideal_relevance = [1.0] * min(len(relevant), k)
        idcg = dcg_at_k(ideal_relevance, k)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _mean_reciprocal_rank(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calculate Mean Reciprocal Rank."""
        if not relevant:
            return 0.0
        
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                return 1.0 / (i + 1)
        return 0.0
    
    def _mean_average_precision(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calculate Mean Average Precision."""
        if not relevant:
            return 0.0
        
        precision_sum = 0.0
        relevant_found = 0
        
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                relevant_found += 1
                precision_at_i = relevant_found / (i + 1)
                precision_sum += precision_at_i
        
        return precision_sum / len(relevant) if relevant else 0.0
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = self._cosine_similarity(embeddings[0], embeddings[1])
            return float(similarity)
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            return float(cosine_similarity([vec1], [vec2])[0][0])
        except Exception:
            # Fallback calculation
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return float(dot_product / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
    
    def _cosine_similarity_matrix(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity matrix between two sets of embeddings."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            return cosine_similarity(embeddings1, embeddings2)
        except Exception:
            # Fallback calculation
            similarities = np.zeros((len(embeddings1), len(embeddings2)))
            for i, emb1 in enumerate(embeddings1):
                for j, emb2 in enumerate(embeddings2):
                    similarities[i, j] = self._cosine_similarity(emb1, emb2)
            return similarities
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text."""
        try:
            import nltk
            sentences = nltk.sent_tokenize(text)
            
            claims = []
            for sentence in sentences:
                # Filter out questions and opinions
                if not any(word in sentence.lower() for word in ['?', 'i think', 'i believe', 'in my opinion']):
                    # Look for factual statements
                    if any(word in sentence.lower() for word in ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'can', 'should']):
                        claims.append(sentence.strip())
            
            return claims
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            return []
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        try:
            import nltk
            return nltk.sent_tokenize(text)
        except Exception:
            # Fallback: simple sentence splitting
            return [s.strip() for s in text.split('.') if s.strip()]
    
    def _calculate_overall_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from individual metrics."""
        try:
            # Weighted combination of key metrics
            weights = {
                "faithfulness_score": 0.3,
                "rouge1": 0.2,
                "semantic_similarity": 0.2,
                "context_utilization": 0.15,
                "precision_at_5": 0.15
            }
            
            score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in metrics and isinstance(metrics[metric], (int, float)):
                    score += metrics[metric] * weight
                    total_weight += weight
            
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Overall quality score calculation failed: {e}")
            return 0.0
    
    def _generate_evaluation_summary(self, aggregate_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate evaluation summary."""
        summary = {
            "evaluation_date": datetime.now().isoformat(),
            "key_metrics": {},
            "performance_level": "unknown"
        }
        
        # Extract key metrics
        key_metrics = ["faithfulness_score", "rouge1", "precision_at_5", "context_utilization"]
        for metric in key_metrics:
            if metric in aggregate_metrics:
                summary["key_metrics"][metric] = aggregate_metrics[metric]["mean"]
        
        # Determine performance level
        if "faithfulness_score" in summary["key_metrics"]:
            faithfulness = summary["key_metrics"]["faithfulness_score"]
            if faithfulness >= 0.8:
                summary["performance_level"] = "excellent"
            elif faithfulness >= 0.6:
                summary["performance_level"] = "good"
            elif faithfulness >= 0.4:
                summary["performance_level"] = "fair"
            else:
                summary["performance_level"] = "poor"
        
        return summary
    
    def _check_regressions(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for regressions compared to baseline."""
        alerts = []
        
        if not self.baseline_metrics:
            return alerts
        
        for metric, current_data in current_metrics.items():
            if metric in self.baseline_metrics and "mean" in current_data:
                baseline_value = self.baseline_metrics[metric]
                current_value = current_data["mean"]
                
                # Calculate percentage change
                if baseline_value > 0:
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                    
                    # Check threshold
                    threshold = self.thresholds.get(metric, 10.0)
                    
                    if change_percent < -threshold:
                        alerts.append({
                            "metric": metric,
                            "baseline": baseline_value,
                            "current": current_value,
                            "change_percent": change_percent,
                            "threshold": threshold,
                            "severity": "high" if change_percent < -20 else "medium"
                        })
        
        return alerts

# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "evaluation_dir": "./evaluations",
        "reports_dir": "./reports",
        "baseline_file": "./baseline_metrics.json",
        "evaluation_thresholds": {
            "faithfulness_score": 10.0,
            "rouge1": 15.0,
            "precision_at_5": 10.0
        }
    }
    
    # Initialize evaluator
    evaluator = ComprehensiveRAGEvaluator(config)
    
    # Example test case
    test_case = {
        "query": "How do I fix vlookup errors?",
        "answer": "Check data types and table references for vlookup errors.",
        "context": "VLOOKUP requires exact data types. Check table references and use FALSE for exact matches.",
        "retrieved_docs": ["excel_guide.md", "troubleshooting.xlsx"],
        "relevant_docs": ["excel_guide.md", "troubleshooting.xlsx"]
    }
    
    # Run evaluation
    results = evaluator.evaluate_end_to_end(
        test_case["query"],
        test_case["answer"],
        test_case["context"],
        test_case["retrieved_docs"],
        test_case["relevant_docs"]
    )
    
    print("Evaluation Results:")
    for key, value in results.items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    print("Comprehensive RAG evaluation test completed successfully!")
