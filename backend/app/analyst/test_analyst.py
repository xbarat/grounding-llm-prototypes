"""Integration tests for analyst module using query processor and pipeline stages"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor
from app.pipeline.optimized_adapters import (
    OptimizedQueryAdapter,
    OptimizedResultAdapter,
    OptimizedValidationAdapter
)
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely
from tests.test_queries import TestQueries

class AnalystMetrics:
    """Tracks metrics for analyst testing"""
    def __init__(self):
        self.total_queries = 0
        self.code_generation_success = 0
        self.code_generation_failure = 0
        self.execution_success = 0
        self.execution_failure = 0
        self.visualization_success = 0
        self.visualization_failure = 0
        self.processing_times: List[float] = []
        self.errors: List[Dict[str, Any]] = []
        
    def record_code_generation_success(self):
        self.code_generation_success += 1
        
    def record_code_generation_failure(self, error: str):
        self.code_generation_failure += 1
        self.errors.append({
            'stage': 'code_generation',
            'error': error
        })
        
    def record_execution_success(self):
        self.execution_success += 1
        
    def record_execution_failure(self, error: str):
        self.execution_failure += 1
        self.errors.append({
            'stage': 'execution',
            'error': error
        })
        
    def record_visualization_success(self):
        self.visualization_success += 1
        
    def record_visualization_failure(self, error: str):
        self.visualization_failure += 1
        self.errors.append({
            'stage': 'visualization',
            'error': error
        })
        
    def record_processing_time(self, time: float):
        self.processing_times.append(time)
        
    def print_summary(self):
        """Print test metrics summary"""
        total_queries = self.code_generation_success + self.code_generation_failure
        self.total_queries = total_queries
        
        print("\n=== Analyst Test Results ===")
        
        print("\nCode Generation:")
        print(f"  Success: {self.code_generation_success}/{total_queries} ({self.code_generation_success/total_queries*100:.1f}%)")
        print(f"  Failure: {self.code_generation_failure}/{total_queries} ({self.code_generation_failure/total_queries*100:.1f}%)")
        
        print("\nCode Execution:")
        print(f"  Success: {self.execution_success}/{total_queries} ({self.execution_success/total_queries*100:.1f}%)")
        print(f"  Failure: {self.execution_failure}/{total_queries} ({self.execution_failure/total_queries*100:.1f}%)")
        
        print("\nVisualization Generation:")
        print(f"  Success: {self.visualization_success}/{total_queries} ({self.visualization_success/total_queries*100:.1f}%)")
        print(f"  Failure: {self.visualization_failure}/{total_queries} ({self.visualization_failure/total_queries*100:.1f}%)")
        
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        print(f"\nPerformance:")
        print(f"  Average Processing Time: {avg_time:.2f} seconds")
        print(f"  Total Tests Run: {total_queries}")
        
        if self.errors:
            print("\nErrors Encountered:")
            for error in self.errors:
                print(f"  - [{error['stage']}] {error['error']}")

async def test_analyst_pipeline(query: str, client: httpx.AsyncClient, metrics: AnalystMetrics) -> bool:
    """Test analyst pipeline using query processor and data pipeline"""
    start_time = datetime.now().timestamp()
    
    try:
        # Stage 1: Process query using QueryProcessor
        print(f"\nProcessing query: {query}")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        if not query_result or not query_result.requirements:
            metrics.record_code_generation_failure("No requirements generated from query")
            return False
            
        # Stage 2: Get data using Pipeline
        season = query_result.requirements.params.get('season', '2023')
        base_url = f"https://ergast.com/api/f1/{season}"
        
        params = {k: v for k, v in query_result.requirements.params.items() if k != 'season'}
        endpoint = query_result.requirements.endpoint.replace('/api/f1', '')
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
            
        url = f"{base_url}/{endpoint}"
        
        print(f"\nFetching data from: {url}")
        if params:
            print(f"With params: {params}")
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        # Convert XML to DataFrame
        from tests.full_test import xml_to_dataframe
        df = xml_to_dataframe(response.text, endpoint)
        
        if df.empty:
            metrics.record_code_generation_failure("No data returned from API")
            return False
            
        # Stage 3: Generate and execute analysis code
        print("\nGenerating analysis code...")
        code_response = generate_code(df, query)
        code_block = extract_code_block(code_response)
        
        if not code_block:
            metrics.record_code_generation_failure("No code block generated")
            return False
            
        metrics.record_code_generation_success()
        
        print("\nExecuting analysis code...")
        success, result, code = execute_code_safely(code_block, df)
        
        if success:
            metrics.record_execution_success()
            print("\nCode executed successfully")
            
            if result.get('figure'):
                metrics.record_visualization_success()
                print("Visualization generated successfully")
            else:
                metrics.record_visualization_failure("No visualization generated")
        else:
            metrics.record_execution_failure(result.get('error', 'Unknown error'))
            print(f"\nExecution error: {result.get('error')}")
            
        processing_time = datetime.now().timestamp() - start_time
        metrics.record_processing_time(processing_time)
        
        return success
        
    except Exception as e:
        error_msg = f"Pipeline Error: {str(e)}\n{traceback.format_exc()}"
        metrics.record_execution_failure(error_msg)
        print(f"Full error for query '{query}': {error_msg}")
        return False

async def run_analyst_tests():
    """Run tests for analyst module using different query categories"""
    metrics = AnalystMetrics()
    
    # Select test queries from different categories
    test_queries = []
    
    # Basic Stats (first 2)
    test_queries.extend(TestQueries.BASIC_STATS.queries[:2])
    
    # Driver Comparisons (first 2)
    test_queries.extend(TestQueries.DRIVER_COMPARISONS.queries[:2])
    
    # Historical Trends (first 2)
    test_queries.extend(TestQueries.HISTORICAL_TRENDS.queries[:2])
    
    print("\nRunning analyst tests with selected queries...")
    print(f"Number of test queries: {len(test_queries)}")
    print("\nQueries to test:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Process test cases in parallel batches
        batch_size = 2  # Smaller batch size due to API rate limits
        for i in range(0, len(test_queries), batch_size):
            batch = test_queries[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}/{(len(test_queries) + batch_size - 1)//batch_size}")
            tasks = [
                test_analyst_pipeline(query, client, metrics)
                for query in batch
            ]
            await asyncio.gather(*tasks)
            print("-" * 80)
    
    metrics.print_summary()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
        
    # Run tests
    asyncio.run(run_analyst_tests()) 