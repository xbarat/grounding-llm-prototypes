"""Integration tests for Pipeline and Analyst components"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor
from app.analyst.generate import generate_code, execute_code_safely
from app.pipeline.optimized_adapters import OptimizedQueryAdapter, OptimizedResultAdapter

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if sys.argv[-1] == "--debug" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineAnalysisMetrics:
    """Track metrics for pipeline-analysis integration"""
    
    def __init__(self):
        self.pipeline_success = 0
        self.pipeline_failure = 0
        self.analysis_success = 0
        self.analysis_failure = 0
        self.total_processing_time = 0.0
        self.query_count = 0
        self.failure_reasons: Dict[str, int] = {}
    
    def record_pipeline_success(self):
        self.pipeline_success += 1
    
    def record_pipeline_failure(self, reason: str):
        self.pipeline_failure += 1
        self.failure_reasons[f"Pipeline: {reason}"] = self.failure_reasons.get(f"Pipeline: {reason}", 0) + 1
    
    def record_analysis_success(self):
        self.analysis_success += 1
    
    def record_analysis_failure(self, reason: str):
        self.analysis_failure += 1
        self.failure_reasons[f"Analysis: {reason}"] = self.failure_reasons.get(f"Analysis: {reason}", 0) + 1
    
    def record_processing_time(self, time: float):
        self.total_processing_time += time
        self.query_count += 1
    
    def print_summary(self):
        """Print test metrics summary"""
        print("\n=== Pipeline-Analysis Integration Test Summary ===")
        
        print("\nPipeline Performance:")
        total_pipeline = self.pipeline_success + self.pipeline_failure
        print(f"  Success: {self.pipeline_success}/{total_pipeline} ({self.pipeline_success/total_pipeline*100:.1f}%)")
        print(f"  Failure: {self.pipeline_failure}/{total_pipeline} ({self.pipeline_failure/total_pipeline*100:.1f}%)")
        
        print("\nAnalysis Performance:")
        total_analysis = self.analysis_success + self.analysis_failure
        print(f"  Success: {self.analysis_success}/{total_analysis} ({self.analysis_success/total_analysis*100:.1f}%)")
        print(f"  Failure: {self.analysis_failure}/{total_analysis} ({self.analysis_failure/total_analysis*100:.1f}%)")
        
        print("\nPerformance Metrics:")
        avg_time = self.total_processing_time / self.query_count if self.query_count > 0 else 0
        print(f"  Average Processing Time: {avg_time:.2f} seconds")
        print(f"  Total Queries Processed: {self.query_count}")
        
        if self.failure_reasons:
            print("\nFailure Reasons:")
            for reason, count in sorted(self.failure_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count}")

metrics = PipelineAnalysisMetrics()

async def test_pipeline_analysis(query: str) -> Optional[Dict[str, Any]]:
    """Test integrated pipeline and analysis workflow"""
    logger.info(f"\nTesting Pipeline-Analysis Integration...")
    logger.info(f"Query: {query}")
    
    start_time = datetime.now().timestamp()
    
    try:
        # Step 1: Process query through pipeline
        logger.info("\nStep 1: Processing query through pipeline...")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        # Step 2: Adapt query result
        logger.info("\nStep 2: Adapting query result...")
        query_adapter = OptimizedQueryAdapter()
        adapted_result = await query_adapter.adapt(query_result)
        
        # Step 3: Process in pipeline
        logger.info("\nStep 3: Processing in pipeline...")
        pipeline = DataPipeline()
        requirements = adapted_result.to_data_requirements()
        pipeline_response = await pipeline.process(requirements)
        
        # Step 4: Adapt pipeline result
        logger.info("\nStep 4: Adapting pipeline result...")
        result_adapter = OptimizedResultAdapter()
        pipeline_result = await result_adapter.adapt_pipeline_result(pipeline_response, start_time)
        
        if not pipeline_result.success:
            metrics.record_pipeline_failure(pipeline_result.error or "Unknown error")
            return None
            
        metrics.record_pipeline_success()
        
        # Step 5: Generate analysis code
        logger.info("\nStep 5: Generating analysis code...")
        if not pipeline_result.data or "results" not in pipeline_result.data:
            metrics.record_analysis_failure("No data available for analysis")
            return None
            
        df = pipeline_result.data["results"]
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        code = generate_code(df, query)
        if not code:
            metrics.record_analysis_failure("Failed to generate analysis code")
            return None
        
        # Step 6: Execute analysis code
        logger.info("\nStep 6: Executing analysis code...")
        success, result, executed_code = execute_code_safely(code, df)
        
        if not success:
            metrics.record_analysis_failure(result.get("error", "Unknown error"))
            return None
            
        metrics.record_analysis_success()
        
        # Record processing time
        processing_time = datetime.now().timestamp() - start_time
        metrics.record_processing_time(processing_time)
        
        return {
            "success": True,
            "pipeline_result": pipeline_result.data,
            "analysis_result": result,
            "executed_code": executed_code,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error in pipeline-analysis integration: {str(e)}")
        return None

async def run_all_tests(test_queries: List[str]):
    """Run all pipeline-analysis integration tests"""
    logger.info("Starting Pipeline-Analysis Integration Tests...")
    logger.info(f"Total queries to test: {len(test_queries)}")
    logger.info("-" * 80)
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\nProcessing query {i}/{len(test_queries)}")
        result = await test_pipeline_analysis(query)
        
        if result:
            logger.info(f"\nSuccess! Processing time: {result['processing_time']:.2f}s")
            logger.debug(f"Executed code:\n{result['executed_code']}")
        else:
            logger.error("Failed to process query")
        
        logger.info("-" * 80)
    
    metrics.print_summary()

if __name__ == "__main__":
    # Test queries focusing on different aspects
    test_queries = [
        # Historical analysis
        "Show Ferrari's performance trend since 2015 with a line plot",
        
        # Multi-driver comparison
        "Create a bar chart comparing pole positions between Max Verstappen and Lewis Hamilton in 2023",
        
        # Constructor analysis
        "Visualize Red Bull's podium finishes from 2010 to 2023 as a time series",
        
        # Statistical analysis
        "Calculate and plot the correlation between qualifying position and race finish position for top drivers in 2023"
    ]
    
    # Run all tests
    asyncio.run(run_all_tests(test_queries)) 