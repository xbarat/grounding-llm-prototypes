"""Test runner for challenging historical and ambiguous queries"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
import httpx
import traceback
from collections import defaultdict
from typing import Union, Dict, Any, List, cast
from datetime import datetime

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor
from app.pipeline.optimized_adapters import (
    OptimizedQueryAdapter,
    OptimizedResultAdapter,
    OptimizedValidationAdapter,
    OptimizedQueryResult,
    OptimizedPipelineResult
)

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
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_processing_time = 0.0
        self.query_count = 0
        # New metrics for tough queries
        self.historical_success = 0
        self.historical_failure = 0
        self.ambiguous_success = 0
        self.ambiguous_failure = 0
        self.entity_resolution_success = 0
        self.entity_resolution_failure = 0
    
    def _safe_percentage(self, part: int, total: int) -> float:
        """Calculate percentage safely handling zero division"""
        return (part / total * 100) if total > 0 else 0.0
    
    def record_historical_success(self):
        self.historical_success += 1
    
    def record_historical_failure(self, reason: str):
        self.historical_failure += 1
        self.failure_reasons[f"Historical: {reason}"] += 1
    
    def record_ambiguous_success(self):
        self.ambiguous_success += 1
    
    def record_ambiguous_failure(self, reason: str):
        self.ambiguous_failure += 1
        self.failure_reasons[f"Ambiguous: {reason}"] += 1
    
    def record_entity_resolution_success(self):
        self.entity_resolution_success += 1
    
    def record_entity_resolution_failure(self, reason: str):
        self.entity_resolution_failure += 1
        self.failure_reasons[f"Entity Resolution: {reason}"] += 1
    
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
    
    def record_cache_hit(self):
        self.cache_hits += 1
    
    def record_cache_miss(self):
        self.cache_misses += 1
    
    def record_processing_time(self, time: float):
        self.total_processing_time += time
        self.query_count += 1
    
    def print_summary(self):
        total_api = self.query_to_json_success + self.query_to_json_failure
        total_df = self.json_to_df_success + self.json_to_df_failure
        total_adapter = self.adapter_success + self.adapter_failure
        total_validation = self.validation_success + self.validation_failure
        total_cache = self.cache_hits + self.cache_misses
        total_historical = self.historical_success + self.historical_failure
        total_ambiguous = self.ambiguous_success + self.ambiguous_failure
        total_entity = self.entity_resolution_success + self.entity_resolution_failure
        avg_processing_time = self.total_processing_time / self.query_count if self.query_count > 0 else 0
        
        print("\n=== Tough Query Test Metrics Summary ===")
        
        print(f"\nHistorical Query Performance:")
        print(f"  Success: {self.historical_success}/{total_historical} ({self._safe_percentage(self.historical_success, total_historical):.1f}%)")
        print(f"  Failure: {self.historical_failure}/{total_historical} ({self._safe_percentage(self.historical_failure, total_historical):.1f}%)")
        
        print(f"\nAmbiguous Query Performance:")
        print(f"  Success: {self.ambiguous_success}/{total_ambiguous} ({self._safe_percentage(self.ambiguous_success, total_ambiguous):.1f}%)")
        print(f"  Failure: {self.ambiguous_failure}/{total_ambiguous} ({self._safe_percentage(self.ambiguous_failure, total_ambiguous):.1f}%)")
        
        print(f"\nEntity Resolution Performance:")
        print(f"  Success: {self.entity_resolution_success}/{total_entity} ({self._safe_percentage(self.entity_resolution_success, total_entity):.1f}%)")
        print(f"  Failure: {self.entity_resolution_failure}/{total_entity} ({self._safe_percentage(self.entity_resolution_failure, total_entity):.1f}%)")
        
        print(f"\nAdapter Performance:")
        print(f"  Success: {self.adapter_success}/{total_adapter} ({self._safe_percentage(self.adapter_success, total_adapter):.1f}%)")
        print(f"  Failure: {self.adapter_failure}/{total_adapter} ({self._safe_percentage(self.adapter_failure, total_adapter):.1f}%)")
        
        print(f"\nValidation Performance:")
        print(f"  Success: {self.validation_success}/{total_validation} ({self._safe_percentage(self.validation_success, total_validation):.1f}%)")
        print(f"  Failure: {self.validation_failure}/{total_validation} ({self._safe_percentage(self.validation_failure, total_validation):.1f}%)")
        
        print(f"\nCache Performance:")
        print(f"  Hits: {self.cache_hits}/{total_cache} ({self._safe_percentage(self.cache_hits, total_cache):.1f}%)")
        print(f"  Misses: {self.cache_misses}/{total_cache} ({self._safe_percentage(self.cache_misses, total_cache):.1f}%)")
        
        print(f"\nQuery → JSON (API Fetch):")
        print(f"  Success: {self.query_to_json_success}/{total_api} ({self._safe_percentage(self.query_to_json_success, total_api):.1f}%)")
        print(f"  Failure: {self.query_to_json_failure}/{total_api} ({self._safe_percentage(self.query_to_json_failure, total_api):.1f}%)")
        
        print(f"\nJSON → DataFrame:")
        print(f"  Success: {self.json_to_df_success}/{total_df} ({self._safe_percentage(self.json_to_df_success, total_df):.1f}%)")
        print(f"  Failure: {self.json_to_df_failure}/{total_df} ({self._safe_percentage(self.json_to_df_failure, total_df):.1f}%)")
        
        print(f"\nPerformance Metrics:")
        print(f"  Average Processing Time: {avg_processing_time:.2f} seconds")
        print(f"  Total Queries Processed: {self.query_count}")
        
        if self.failure_reasons:
            print("\nFailure Reasons:")
            for reason, count in sorted(self.failure_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count}")

metrics = TestMetrics()

async def test_integrated_pipeline(query: str, query_type: str, client: httpx.AsyncClient) -> Union[pd.DataFrame, Dict[str, Any]]:
    """Test the integrated pipeline with optimized adapters."""
    print(f"\nTesting {query_type} query: {query}")
    
    start_time = datetime.now().timestamp()
    
    try:
        # Step 1: Process query
        print("\nStep 1: Processing query...")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        # Step 2: Adapt query result with optimized adapter
        print("\nStep 2: Adapting query result...")
        query_adapter = OptimizedQueryAdapter()
        validation_adapter = OptimizedValidationAdapter()
        
        try:
            adapted_result = await query_adapter.adapt(query_result)
            validation_results = await validation_adapter.validate_batch([adapted_result])
            if validation_results and validation_results[0]:
                metrics.record_adapter_success()
                metrics.record_validation_success()
                if adapted_result.cache_hit:
                    metrics.record_cache_hit()
                else:
                    metrics.record_cache_miss()
            else:
                metrics.record_validation_failure("Invalid adapted result")
                return pd.DataFrame()
        except Exception as e:
            metrics.record_adapter_failure(str(e))
            print(f"Adapter error: {str(e)}")
            return pd.DataFrame()
        
        # Step 3: Convert to pipeline format
        print("\nStep 3: Converting to pipeline format...")
        requirements = adapted_result.to_data_requirements()
        
        # Step 4: Process in pipeline
        print("\nStep 4: Processing in pipeline...")
        pipeline = DataPipeline()
        response = await pipeline.process(requirements)
        
        # Step 5: Adapt pipeline result with optimized adapter
        print("\nStep 5: Adapting pipeline result...")
        result_adapter = OptimizedResultAdapter()
        
        try:
            pipeline_result = await result_adapter.adapt_pipeline_result(response, start_time)
            validation_results = await validation_adapter.validate_batch([pipeline_result])
            if validation_results and validation_results[0]:
                metrics.record_validation_success()
                if pipeline_result.cache_hit:
                    metrics.record_cache_hit()
                else:
                    metrics.record_cache_miss()
            else:
                metrics.record_validation_failure("Invalid pipeline result")
                return pd.DataFrame()
        except Exception as e:
            metrics.record_adapter_failure(str(e))
            print(f"Pipeline result adapter error: {str(e)}")
            return pd.DataFrame()
        
        # Record processing time
        processing_time = datetime.now().timestamp() - start_time
        metrics.record_processing_time(processing_time)
        
        # Record query type specific metrics
        if query_type == "historical":
            if pipeline_result.success:
                metrics.record_historical_success()
            else:
                metrics.record_historical_failure(pipeline_result.error or "Unknown error")
        elif query_type == "ambiguous":
            if pipeline_result.success:
                metrics.record_ambiguous_success()
            else:
                metrics.record_ambiguous_failure(pipeline_result.error or "Unknown error")
        
        # Record entity resolution if applicable
        if "entities" in pipeline_result.metadata:
            if pipeline_result.success:
                metrics.record_entity_resolution_success()
            else:
                metrics.record_entity_resolution_failure(pipeline_result.error or "Unknown error")
        
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

async def run_all_tests(historical_queries: List[str], ambiguous_queries: List[str]):
    """Run all tests using a single event loop and shared client"""
    print("Starting test of tough queries...")
    print(f"Total historical queries: {len(historical_queries)}")
    print(f"Total ambiguous queries: {len(ambiguous_queries)}")
    print("-" * 80)
    
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        # Process historical queries in parallel batches
        batch_size = 4
        for i in range(0, len(historical_queries), batch_size):
            batch = historical_queries[i:i + batch_size]
            print(f"\nProcessing historical batch {i//batch_size + 1}/{(len(historical_queries) + batch_size - 1)//batch_size}")
            tasks = [test_integrated_pipeline(query, "historical", client) for query in batch]
            await asyncio.gather(*tasks)
            print("-" * 80)
        
        # Process ambiguous queries in parallel batches
        for i in range(0, len(ambiguous_queries), batch_size):
            batch = ambiguous_queries[i:i + batch_size]
            print(f"\nProcessing ambiguous batch {i//batch_size + 1}/{(len(ambiguous_queries) + batch_size - 1)//batch_size}")
            tasks = [test_integrated_pipeline(query, "ambiguous", client) for query in batch]
            await asyncio.gather(*tasks)
            print("-" * 80)
    
    metrics.print_summary()

if __name__ == "__main__":
    # Historical queries
    historical_queries = [
        "How has Mercedes' win rate changed since 2010?",
        "Which driver has won the most races in wet conditions since 2005?",
        "What are Red Bull's podium finishes by year from 2015 to 2023?",
        "How many races has Hamilton won each season since 2014?",
        "Which team dominated constructors' championships from 2000 to 2010?",
        "Show the fastest lap times in Monaco for each season since 2010.",
        "How many DNFs has Ferrari had in the last 5 seasons?",
        "What is the historical trend for fastest laps set by Verstappen since his debut?",
        "How many pole positions did Red Bull achieve during the Vettel era (2010-2013)?",
        "Which driver has the most points without winning a championship since 1990?"
    ]
    
    # Ambiguous queries
    ambiguous_queries = [
        "Which driver performs best in the rain?",
        "Who is the fastest driver in Monaco?",
        "What team has improved the most over the last 5 seasons?",
        "Which constructor is the best on street circuits?",
        "What is Hamilton's success rate at circuits where Verstappen also won?",
        "Which races had the closest finishes in F1 history?",
        "How does Ferrari perform compared to Red Bull in wet conditions?",
        "What is the average finishing position for Alonso in 2023?",
        "Which races had safety cars deployed in 2022?",
        "Who are the best drivers on tire conservation strategies?"
    ]
    
    # Run all tests in a single event loop with parallel processing
    asyncio.run(run_all_tests(historical_queries, ambiguous_queries)) 