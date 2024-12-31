import asyncio
import sys
from pathlib import Path
import pandas as pd
import httpx
import traceback
from collections import defaultdict
from typing import Union, Dict, Any

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline, DataTransformer
from app.query.processor import QueryProcessor, DataRequirements

class TestMetrics:
    def __init__(self):
        self.query_to_json_success = 0
        self.query_to_json_failure = 0
        self.json_to_df_success = 0
        self.json_to_df_failure = 0
        self.failure_reasons = defaultdict(int)
    
    def record_api_success(self):
        self.query_to_json_success += 1
    
    def record_api_failure(self, reason):
        self.query_to_json_failure += 1
        self.failure_reasons[f"API: {reason}"] += 1
    
    def record_df_success(self):
        self.json_to_df_success += 1
    
    def record_df_failure(self, reason):
        self.json_to_df_failure += 1
        self.failure_reasons[f"DataFrame: {reason}"] += 1
    
    def print_summary(self):
        total_api = self.query_to_json_success + self.query_to_json_failure
        total_df = self.json_to_df_success + self.json_to_df_failure
        
        print("\n=== Test Metrics Summary ===")
        print(f"Query → JSON (API Fetch):")
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
    """Test the integrated pipeline with a query."""
    print("\nTesting integrated pipeline...")
    print(f"Query: {query}")
    
    print("\nStep 1: Processing query...")
    processor = QueryProcessor()
    requirements = await processor.process_query(query)
    if not requirements:
        return pd.DataFrame()
    
    print("\nStep 2: Fetching and processing data...")
    pipeline = DataPipeline()
    response = await pipeline.process(requirements)
    
    # Return the raw DataFrame for validation
    if response.success and response.data is not None:
        metrics.record_api_success()
        df = response.data["results"]
        if not df.empty:
            metrics.record_df_success()
            return df
        else:
            metrics.record_df_failure("Empty DataFrame")
    else:
        metrics.record_api_failure(response.error or "Unknown error")
    
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