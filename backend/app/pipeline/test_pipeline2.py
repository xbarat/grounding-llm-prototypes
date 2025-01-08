"""Test pipeline with adapters for Q2 system"""
import asyncio
import sys
from pathlib import Path
import pandas as pd
import httpx
import traceback
from collections import defaultdict
from typing import Union, Dict, Any
from datetime import datetime

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor
from app.pipeline.adapters import QueryResultAdapter, ResultAdapter, ValidationAdapter, PipelineResult

class TestMetrics:
    def __init__(self):
        self.query_to_json_success = 0
        self.query_to_json_failure = 0
        self.json_to_df_success = 0
        self.json_to_df_failure = 0
        self.failure_reasons = defaultdict(int)
        self.adapter_success = 0
        self.adapter_failure = 0
        self.validation_success = 0
        self.validation_failure = 0
    
    def record_adapter_success(self):
        self.adapter_success += 1
    
    def record_adapter_failure(self, reason: str):
        self.adapter_failure += 1
        self.failure_reasons[f"Adapter: {reason}"] += 1
    
    def record_validation_success(self):
        self.validation_success += 1
    
    def record_validation_failure(self, reason: str):
        self.validation_failure += 1
        self.failure_reasons[f"Validation: {reason}"] += 1
    
    def record_api_success(self):
        self.query_to_json_success += 1
    
    def record_api_failure(self, reason: str):
        self.query_to_json_failure += 1
        self.failure_reasons[f"API: {reason}"] += 1
    
    def record_df_success(self):
        self.json_to_df_success += 1
    
    def record_df_failure(self, reason: str):
        self.json_to_df_failure += 1
        self.failure_reasons[f"DataFrame: {reason}"] += 1
    
    def print_summary(self):
        total_api = self.query_to_json_success + self.query_to_json_failure
        total_df = self.json_to_df_success + self.json_to_df_failure
        total_adapter = self.adapter_success + self.adapter_failure
        total_validation = self.validation_success + self.validation_failure
        
        print("\n=== Test Metrics Summary ===")
        
        print(f"\nAdapter Performance:")
        print(f"  Success: {self.adapter_success}/{total_adapter} ({(self.adapter_success/total_adapter*100):.1f}%)")
        print(f"  Failure: {self.adapter_failure}/{total_adapter} ({(self.adapter_failure/total_adapter*100):.1f}%)")
        
        print(f"\nValidation Performance:")
        print(f"  Success: {self.validation_success}/{total_validation} ({(self.validation_success/total_validation*100):.1f}%)")
        print(f"  Failure: {self.validation_failure}/{total_validation} ({(self.validation_failure/total_validation*100):.1f}%)")
        
        print(f"\nQuery → JSON (API Fetch):")
        print(f"  Success: {self.query_to_json_success}/{total_api} ({(self.query_to_json_success/total_api*100):.1f}%)")
        print(f"  Failure: {self.query_to_json_failure}/{total_api} ({(self.query_to_json_failure/total_api*100):.1f}%)")
        
        print(f"\nJSON → DataFrame:")
        print(f"  Success: {self.json_to_df_success}/{total_df} ({(self.json_to_df_success/total_df*100):.1f}%)")
        print(f"  Failure: {self.json_to_df_failure}/{total_df} ({(self.json_to_df_failure/total_df*100):.1f}%)")
        
        if self.failure_reasons:
            print("\nFailure Reasons:")
            for reason, count in sorted(self.failure_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count}")

metrics = TestMetrics()

async def test_integrated_pipeline(query: str, client: httpx.AsyncClient) -> Union[pd.DataFrame, Dict[str, Any]]:
    """Test the integrated pipeline with a query using adapters."""
    print("\nTesting integrated pipeline...")
    print(f"Query: {query}")
    
    try:
        # Step 1: Process query
        print("\nStep 1: Processing query...")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        # Step 2: Adapt query result
        print("\nStep 2: Adapting query result...")
        try:
            adapted_result = QueryResultAdapter.adapt(query_result)
            if ValidationAdapter.validate_query_result(adapted_result):
                metrics.record_adapter_success()
                metrics.record_validation_success()
            else:
                metrics.record_validation_failure("Invalid adapted result")
                return pd.DataFrame()
        except Exception as e:
            metrics.record_adapter_failure(str(e))
            print(f"Adapter error: {str(e)}")
            return pd.DataFrame()
        
        # Step 3: Convert to pipeline format
        print("\nStep 3: Converting to pipeline format...")
        requirements = QueryResultAdapter.to_pipeline_format(adapted_result)
        
        # Step 4: Process in pipeline
        print("\nStep 4: Processing in pipeline...")
        pipeline = DataPipeline()
        response = await pipeline.process(requirements)
        
        # Step 5: Adapt pipeline result
        print("\nStep 5: Adapting pipeline result...")
        try:
            pipeline_result = ResultAdapter.adapt_pipeline_result(response)
            if ValidationAdapter.validate_pipeline_result(pipeline_result):
                metrics.record_validation_success()
            else:
                metrics.record_validation_failure("Invalid pipeline result")
                return pd.DataFrame()
        except Exception as e:
            metrics.record_adapter_failure(str(e))
            print(f"Pipeline result adapter error: {str(e)}")
            return pd.DataFrame()
        
        # Return the processed data
        if pipeline_result.success and pipeline_result.data is not None:
            metrics.record_api_success()
            df = pipeline_result.data.get("results", pd.DataFrame())
            if not df.empty:
                metrics.record_df_success()
                return df
            else:
                metrics.record_df_failure("Empty DataFrame")
        else:
            metrics.record_api_failure(pipeline_result.error or "Unknown error")
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

async def run_all_tests(test_queries):
    """Run all tests using a single event loop and shared client"""
    print("Starting test of all queries...")
    print(f"Total queries to test: {len(test_queries)}")
    print("-" * 80)
    
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for i, query in enumerate(test_queries, 1):
            print(f"\nTesting query {i}/{len(test_queries)}")
            print("-" * 40)
            await test_integrated_pipeline(query, client)
            print("-" * 80)
    
    metrics.print_summary()

if __name__ == "__main__":
    # Test queries focusing on different aspects
    test_queries = [
        # Basic performance queries
        "How has Max Verstappen performed in the 2023 season?",
        "What are Lewis Hamilton's stats for 2023?",
        
        # Qualifying specific queries
        "What was Charles Leclerc's qualifying position in Monaco 2023?",
        "Show me Oscar Piastri's qualifying results for 2023",
        
        # Race performance queries
        "How many podiums did Fernando Alonso get in 2023?",
        "What's Lando Norris's average finishing position in 2023?",
        
        # Circuit specific queries
        "How did George Russell perform at Silverstone in 2023?",
        "Show me Carlos Sainz's results at Monza 2023"
    ]
    
    # Run all tests in a single event loop
    asyncio.run(run_all_tests(test_queries)) 