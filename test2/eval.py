"""Evaluation module for Pipeline-Analysis system quality metrics"""

import asyncio
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineAnalysisEvaluator:
    """Evaluator for Pipeline-Analysis system performance and quality"""
    
    def __init__(self):
        self.metrics = {
            # Connection Points
            "endpoint_success_rate": 0.0,
            "api_success_rate": 0.0,
            "pipeline_success_rate": 0.0,
            "analysis_success_rate": 0.0,
            
            # Data Quality
            "null_rate": 0.0,
            "data_completeness": 0.0,
            "data_consistency": 0.0,
            
            # Performance
            "avg_response_time": 0.0,
            "avg_processing_time": 0.0,
            "memory_usage": 0.0,
            
            # Output Quality
            "visualization_score": 0.0,
            "analysis_accuracy": 0.0,
            "code_quality_score": 0.0
        }
        
        self.detailed_logs = []
        self.error_logs = []
        
    async def evaluate_query(self, query: str, result: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a single query execution"""
        metrics = {}
        
        try:
            # 1. Connection Points
            metrics["endpoint_success"] = self._evaluate_endpoint(result)
            metrics["api_success"] = self._evaluate_api(result)
            metrics["pipeline_success"] = self._evaluate_pipeline(result)
            metrics["analysis_success"] = self._evaluate_analysis(result)
            
            # 2. Data Quality
            if "pipeline_result" in result:
                data_quality = self._evaluate_data_quality(result["pipeline_result"])
                metrics.update(data_quality)
            
            # 3. Performance
            if "processing_time" in result:
                metrics["processing_time"] = result["processing_time"]
            
            # 4. Output Quality
            if "analysis_result" in result:
                output_quality = self._evaluate_output_quality(result["analysis_result"])
                metrics.update(output_quality)
            
            # Log successful evaluation
            self.detailed_logs.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "metrics": metrics
            })
            
        except Exception as e:
            logger.error(f"Error evaluating query: {str(e)}")
            self.error_logs.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "error": str(e)
            })
            
        return metrics
    
    def _evaluate_endpoint(self, result: Dict[str, Any]) -> float:
        """Evaluate endpoint connection success"""
        if not result.get("pipeline_result"):
            return 0.0
            
        # Check if endpoint returned valid data structure
        try:
            data = result["pipeline_result"]
            if isinstance(data, dict) and "results" in data:
                return 1.0
            return 0.5  # Partial success
        except:
            return 0.0
    
    def _evaluate_api(self, result: Dict[str, Any]) -> float:
        """Evaluate API response quality"""
        if not result.get("pipeline_result"):
            return 0.0
            
        try:
            data = result["pipeline_result"]
            # Check for common API response indicators
            has_data = bool(data.get("results"))
            has_metadata = bool(data.get("metadata"))
            has_error = bool(data.get("error"))
            
            if has_data and has_metadata and not has_error:
                return 1.0
            elif has_data and not has_error:
                return 0.75
            elif has_error:
                return 0.0
            return 0.5
        except:
            return 0.0
    
    def _evaluate_pipeline(self, result: Dict[str, Any]) -> float:
        """Evaluate pipeline processing success"""
        if not result.get("pipeline_result"):
            return 0.0
            
        try:
            data = result["pipeline_result"]["results"]
            if isinstance(data, (pd.DataFrame, list, dict)):
                if len(data) > 0:
                    return 1.0
                return 0.5
            return 0.0
        except:
            return 0.0
    
    def _evaluate_analysis(self, result: Dict[str, Any]) -> float:
        """Evaluate analysis output quality"""
        if not result.get("analysis_result"):
            return 0.0
            
        try:
            analysis = result["analysis_result"]
            has_figure = bool(analysis.get("figure"))
            has_output = bool(analysis.get("output"))
            has_data = bool(analysis.get("data"))
            
            if has_figure and has_output and has_data:
                return 1.0
            elif has_figure and has_output:
                return 0.75
            elif has_figure or has_output:
                return 0.5
            return 0.0
        except:
            return 0.0
    
    def _evaluate_data_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate quality of processed data"""
        metrics = {
            "null_rate": 0.0,
            "data_completeness": 0.0,
            "data_consistency": 0.0
        }
        
        try:
            if "results" not in data:
                return metrics
                
            df = pd.DataFrame(data["results"])
            
            # Calculate null rate
            null_rate = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
            metrics["null_rate"] = 1.0 - null_rate
            
            # Calculate data completeness
            required_columns = {"year", "ConstructorTable"}  # Add more as needed
            has_required = all(col in df.columns for col in required_columns)
            metrics["data_completeness"] = 1.0 if has_required else 0.5
            
            # Check data consistency
            metrics["data_consistency"] = self._check_data_consistency(df)
            
        except Exception as e:
            logger.error(f"Error in data quality evaluation: {str(e)}")
            
        return metrics
    
    def _check_data_consistency(self, df: pd.DataFrame) -> float:
        """Check consistency of data types and values"""
        try:
            # Check year consistency
            if "year" in df.columns:
                year_valid = df["year"].between(1950, 2024).all()
                return 1.0 if year_valid else 0.5
        except:
            pass
        return 0.0
    
    def _evaluate_output_quality(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate quality of analysis output"""
        metrics = {
            "visualization_score": 0.0,
            "analysis_accuracy": 0.0,
            "code_quality_score": 0.0
        }
        
        try:
            # Check visualization
            if result.get("figure"):
                metrics["visualization_score"] = 1.0
                
            # Check analysis output
            if result.get("output"):
                metrics["analysis_accuracy"] = 1.0
                
            # Check code quality
            if result.get("executed_code"):
                code_quality = self._evaluate_code_quality(result["executed_code"])
                metrics["code_quality_score"] = code_quality
                
        except Exception as e:
            logger.error(f"Error in output quality evaluation: {str(e)}")
            
        return metrics
    
    def _evaluate_code_quality(self, code: str) -> float:
        """Evaluate quality of generated code"""
        score = 0.0
        total_checks = 4
        
        # Check for proper imports
        if all(imp in code for imp in ["pandas", "matplotlib", "seaborn"]):
            score += 0.25
            
        # Check for error handling
        if "try:" in code and "except:" in code:
            score += 0.25
            
        # Check for data validation
        if "if" in code and any(check in code for check in ["is None", "len(", "isnull"]):
            score += 0.25
            
        # Check for proper documentation
        if "#" in code and "summary" in code.lower():
            score += 0.25
            
        return score
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all evaluations"""
        if not self.detailed_logs:
            return {"error": "No evaluations performed"}
            
        metrics_df = pd.DataFrame([log["metrics"] for log in self.detailed_logs])
        
        summary = {
            "total_queries": len(self.detailed_logs),
            "success_rate": metrics_df["analysis_success"].mean(),
            "avg_processing_time": metrics_df["processing_time"].mean(),
            "data_quality": {
                "null_rate": metrics_df["null_rate"].mean(),
                "completeness": metrics_df["data_completeness"].mean(),
                "consistency": metrics_df["data_consistency"].mean()
            },
            "performance": {
                "endpoint_success": metrics_df["endpoint_success"].mean(),
                "api_success": metrics_df["api_success"].mean(),
                "pipeline_success": metrics_df["pipeline_success"].mean()
            },
            "output_quality": {
                "visualization": metrics_df["visualization_score"].mean(),
                "analysis": metrics_df["analysis_accuracy"].mean(),
                "code_quality": metrics_df["code_quality_score"].mean()
            },
            "error_rate": len(self.error_logs) / len(self.detailed_logs)
        }
        
        return summary
    
    def save_results(self, output_dir: str = "evaluation_results"):
        """Save evaluation results to files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save summary
        summary = self.get_summary()
        with open(f"{output_dir}/summary.json", "w") as f:
            json.dump(summary, f, indent=2)
            
        # Save detailed logs
        with open(f"{output_dir}/detailed_logs.json", "w") as f:
            json.dump(self.detailed_logs, f, indent=2)
            
        # Save error logs
        with open(f"{output_dir}/error_logs.json", "w") as f:
            json.dump(self.error_logs, f, indent=2)
            
        logger.info(f"Evaluation results saved to {output_dir}/")

async def run_evaluation(queries: List[str]):
    """Run evaluation on a set of queries"""
    from backend.test2.test_pipeline_analysis import test_pipeline_analysis
    
    evaluator = PipelineAnalysisEvaluator()
    
    for query in queries:
        logger.info(f"Evaluating query: {query}")
        result = await test_pipeline_analysis(query)
        if result:
            metrics = await evaluator.evaluate_query(query, result)
            logger.info(f"Metrics: {metrics}")
    
    summary = evaluator.get_summary()
    logger.info("\nEvaluation Summary:")
    logger.info(json.dumps(summary, indent=2))
    
    # Save results
    evaluator.save_results()

if __name__ == "__main__":
    # Example query set
    test_queries = [
        # Basic queries
        "Show Ferrari's performance in 2023",
        "Compare Red Bull and Mercedes points in 2022",
        
        # Complex queries
        "Analyze the correlation between qualifying and race positions for top teams",
        "Show the trend of DNFs across seasons from 2015 to 2023",
        
        # Edge cases
        "Compare non-existent team performance",
        "Analyze results from invalid season 2025"
    ]
    
    asyncio.run(run_evaluation(test_queries)) 