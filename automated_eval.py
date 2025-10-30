"""
Automated RAG Evaluation Pipeline for Chunker_v2
Runs evaluations on schedule and generates reports
"""

import os
import json
import logging
import schedule
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class AutomatedEvaluator:
    """
    Automated evaluation system for RAG pipeline.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize automated evaluator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.evaluation_dir = config.get("evaluation_dir", "./evaluations")
        self.reports_dir = config.get("reports_dir", "./reports")
        self.baseline_file = config.get("baseline_file", "./baseline_metrics.json")
        self.alert_thresholds = config.get("alert_thresholds", {})
        
        # Create directories
        os.makedirs(self.evaluation_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Load baseline metrics
        self.baseline_metrics = self._load_baseline_metrics()
        
        logger.info("Initialized automated evaluator")
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """
        Load baseline metrics for comparison.
        
        Returns:
            Baseline metrics dictionary
        """
        try:
            if os.path.exists(self.baseline_file):
                with open(self.baseline_file, 'r') as f:
                    baseline = json.load(f)
                logger.info("Loaded baseline metrics")
                return baseline
            else:
                logger.info("No baseline metrics found, will create after first evaluation")
                return {}
        except Exception as e:
            logger.error(f"Failed to load baseline metrics: {e}")
            return {}
    
    def _save_baseline_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Save baseline metrics.
        
        Args:
            metrics: Metrics to save as baseline
        """
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info("Saved baseline metrics")
        except Exception as e:
            logger.error(f"Failed to save baseline metrics: {e}")
    
    def run_evaluation(self, rag_system, test_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run evaluation on test queries.
        
        Args:
            rag_system: RAG system to evaluate
            test_queries: List of test queries
            
        Returns:
            Evaluation results
        """
        try:
            from rag_evaluation import RAGEvaluator, run_evaluation_pipeline
            
            # Initialize evaluator
            evaluator = RAGEvaluator()
            
            # Run evaluation pipeline
            results = run_evaluation_pipeline(test_queries, rag_system, evaluator)
            
            # Calculate aggregate metrics
            aggregate_metrics = self._calculate_aggregate_metrics(results)
            
            # Check for regressions
            regression_alerts = self._check_regressions(aggregate_metrics)
            
            # Generate report
            report = self._generate_report(results, aggregate_metrics, regression_alerts)
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(self.evaluation_dir, f"evaluation_{timestamp}.json")
            self._save_evaluation_results(results, results_file)
            
            # Save report
            report_file = os.path.join(self.reports_dir, f"report_{timestamp}.json")
            self._save_report(report, report_file)
            
            # Update baseline if this is the first evaluation
            if not self.baseline_metrics:
                self.baseline_metrics = aggregate_metrics
                self._save_baseline_metrics(aggregate_metrics)
                logger.info("Set initial baseline metrics")
            
            # Send alerts if needed
            if regression_alerts:
                self._send_alerts(regression_alerts)
            
            logger.info(f"Evaluation completed: {timestamp}")
            return report
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_aggregate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate aggregate metrics from individual results.
        
        Args:
            results: List of individual evaluation results
            
        Returns:
            Aggregate metrics dictionary
        """
        if not results:
            return {}
        
        # Extract numeric metrics
        numeric_metrics = {}
        for result in results:
            if result.get("success", True):  # Skip failed results
                for key, value in result.items():
                    if isinstance(value, (int, float)) and key not in ["test_case_id"]:
                        if key not in numeric_metrics:
                            numeric_metrics[key] = []
                        numeric_metrics[key].append(value)
        
        # Calculate aggregate statistics
        aggregate_metrics = {}
        for metric, values in numeric_metrics.items():
            if values:
                aggregate_metrics[f"{metric}_mean"] = sum(values) / len(values)
                aggregate_metrics[f"{metric}_min"] = min(values)
                aggregate_metrics[f"{metric}_max"] = max(values)
                aggregate_metrics[f"{metric}_count"] = len(values)
        
        return aggregate_metrics
    
    def _check_regressions(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Check for regressions compared to baseline.
        
        Args:
            current_metrics: Current evaluation metrics
            
        Returns:
            List of regression alerts
        """
        alerts = []
        
        if not self.baseline_metrics:
            return alerts
        
        for metric, current_value in current_metrics.items():
            if metric.endswith("_mean") and metric in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric]
                
                # Calculate percentage change
                if baseline_value > 0:
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                    
                    # Check if regression exceeds threshold
                    threshold = self.alert_thresholds.get(metric, 10.0)  # Default 10% threshold
                    
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
    
    def _generate_report(self, results: List[Dict[str, Any]], 
                        aggregate_metrics: Dict[str, float], 
                        regression_alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate evaluation report.
        
        Args:
            results: Individual evaluation results
            aggregate_metrics: Aggregate metrics
            regression_alerts: Regression alerts
            
        Returns:
            Evaluation report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(results),
            "successful_queries": sum(1 for r in results if r.get("success", True)),
            "failed_queries": sum(1 for r in results if not r.get("success", True)),
            "aggregate_metrics": aggregate_metrics,
            "regression_alerts": regression_alerts,
            "baseline_metrics": self.baseline_metrics,
            "summary": self._generate_summary(aggregate_metrics, regression_alerts)
        }
        
        return report
    
    def _generate_summary(self, aggregate_metrics: Dict[str, float], 
                         regression_alerts: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable summary.
        
        Args:
            aggregate_metrics: Aggregate metrics
            regression_alerts: Regression alerts
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Overall performance
        if "precision_at_5_mean" in aggregate_metrics:
            precision = aggregate_metrics["precision_at_5_mean"]
            summary_parts.append(f"Average Precision@5: {precision:.3f}")
        
        if "recall_at_5_mean" in aggregate_metrics:
            recall = aggregate_metrics["recall_at_5_mean"]
            summary_parts.append(f"Average Recall@5: {recall:.3f}")
        
        if "faithfulness_mean" in aggregate_metrics:
            faithfulness = aggregate_metrics["faithfulness_mean"]
            summary_parts.append(f"Average Faithfulness: {faithfulness:.3f}")
        
        # Regression alerts
        if regression_alerts:
            summary_parts.append(f"⚠️ {len(regression_alerts)} regression(s) detected")
        else:
            summary_parts.append("✅ No regressions detected")
        
        return " | ".join(summary_parts)
    
    def _save_evaluation_results(self, results: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save evaluation results to file.
        
        Args:
            results: Evaluation results
            file_path: Output file path
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved evaluation results to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save evaluation results: {e}")
    
    def _save_report(self, report: Dict[str, Any], file_path: str) -> None:
        """
        Save evaluation report to file.
        
        Args:
            report: Evaluation report
            file_path: Output file path
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved evaluation report to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save evaluation report: {e}")
    
    def _send_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """
        Send regression alerts.
        
        Args:
            alerts: List of regression alerts
        """
        try:
            # Log alerts
            for alert in alerts:
                logger.warning(f"Regression detected: {alert['metric']} "
                             f"({alert['change_percent']:.1f}% change)")
            
            # TODO: Implement email/Slack notifications
            # This would integrate with the existing notification system
            
        except Exception as e:
            logger.error(f"Failed to send alerts: {e}")
    
    def generate_csv_report(self, days: int = 7) -> str:
        """
        Generate CSV report for the last N days.
        
        Args:
            days: Number of days to include
            
        Returns:
            Path to generated CSV file
        """
        try:
            # Find evaluation files from the last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            evaluation_files = []
            
            for file in os.listdir(self.evaluation_dir):
                if file.startswith("evaluation_") and file.endswith(".json"):
                    file_path = os.path.join(self.evaluation_dir, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time >= cutoff_date:
                        evaluation_files.append(file_path)
            
            # Load and combine data
            all_results = []
            for file_path in evaluation_files:
                with open(file_path, 'r') as f:
                    results = json.load(f)
                    all_results.extend(results)
            
            # Convert to DataFrame
            df = pd.DataFrame(all_results)
            
            # Generate CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(self.reports_dir, f"evaluation_summary_{timestamp}.csv")
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Generated CSV report: {csv_path}")
            return csv_path
            
        except Exception as e:
            logger.error(f"Failed to generate CSV report: {e}")
            return ""
    
    def cleanup_old_files(self, days: int = 30) -> None:
        """
        Clean up old evaluation files.
        
        Args:
            days: Number of days to keep files
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean evaluation files
            for file in os.listdir(self.evaluation_dir):
                file_path = os.path.join(self.evaluation_dir, file)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Removed old evaluation file: {file}")
            
            # Clean report files
            for file in os.listdir(self.reports_dir):
                file_path = os.path.join(self.reports_dir, file)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Removed old report file: {file}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")

def run_scheduled_evaluation(config: Dict[str, Any], rag_system, test_queries: List[Dict[str, Any]]) -> None:
    """
    Run scheduled evaluation.
    
    Args:
        config: Configuration dictionary
        rag_system: RAG system to evaluate
        test_queries: Test queries
    """
    try:
        evaluator = AutomatedEvaluator(config)
        report = evaluator.run_evaluation(rag_system, test_queries)
        
        logger.info("Scheduled evaluation completed")
        logger.info(f"Summary: {report.get('summary', 'No summary available')}")
        
    except Exception as e:
        logger.error(f"Scheduled evaluation failed: {e}")

def start_automated_evaluation(config: Dict[str, Any], rag_system, test_queries: List[Dict[str, Any]]) -> None:
    """
    Start automated evaluation scheduler.
    
    Args:
        config: Configuration dictionary
        rag_system: RAG system to evaluate
        test_queries: Test queries
    """
    # Schedule evaluations
    schedule.every().day.at("02:00").do(run_scheduled_evaluation, config, rag_system, test_queries)
    schedule.every().monday.at("09:00").do(lambda: AutomatedEvaluator(config).generate_csv_report(days=7))
    schedule.every().month.do(lambda: AutomatedEvaluator(config).cleanup_old_files(days=30))
    
    logger.info("Started automated evaluation scheduler")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "evaluation_dir": "./evaluations",
        "reports_dir": "./reports",
        "baseline_file": "./baseline_metrics.json",
        "alert_thresholds": {
            "precision_at_5_mean": 10.0,
            "recall_at_5_mean": 10.0,
            "faithfulness_mean": 15.0
        }
    }
    
    # Sample test queries
    test_queries = [
        {
            "query": "How do I fix vlookup errors?",
            "expected_answer": "Check data types and table references",
            "expected_sources": ["excel_guide.md", "troubleshooting.xlsx"]
        }
    ]
    
    # Initialize evaluator
    evaluator = AutomatedEvaluator(config)
    
    # Run evaluation (would normally use real RAG system)
    print("Automated evaluation test completed successfully!")
