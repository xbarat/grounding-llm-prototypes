I'll start with implementing the adapters and updating the test pipeline to validate the approach.

```python:backend/app/pipeline/adapters.py
"""
Adapters for Q2 Pipeline System
Handles conversions between different data types and formats in the pipeline.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union
from ..query.processor import ProcessingResult
from ..query.models import DataRequirements

@dataclass
class AdaptedQueryResult:
    """Unified format for query results throughout the pipeline"""
    endpoint: str
    params: Dict[str, Any]
    metadata: Dict[str, Any]
    source_type: str
    
    @classmethod
    def from_processing_result(cls, result: ProcessingResult) -> "AdaptedQueryResult":
        """Convert ProcessingResult to AdaptedQueryResult"""
        return cls(
            endpoint=result.requirements.endpoint,
            params=result.requirements.params,
            metadata={
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "source": result.source
            },
            source_type="processing_result"
        )
    
    def to_data_requirements(self) -> DataRequirements:
        """Convert to DataRequirements for pipeline processing"""
        return DataRequirements(
            endpoint=self.endpoint,
            params=self.params
        )

class QueryResultAdapter:
    """Adapter for query processing results"""
    
    @staticmethod
    def adapt(result: Union[ProcessingResult, Dict[str, Any]]) -> AdaptedQueryResult:
        """Adapt various input types to unified format"""
        if isinstance(result, ProcessingResult):
            return AdaptedQueryResult.from_processing_result(result)
        elif isinstance(result, dict):
            return AdaptedQueryResult(
                endpoint=result.get("endpoint", ""),
                params=result.get("params", {}),
                metadata=result.get("metadata", {}),
                source_type="dict"
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")
    
    @staticmethod
    def to_pipeline_format(result: AdaptedQueryResult) -> DataRequirements:
        """Convert adapted result to pipeline-compatible format"""
        return result.to_data_requirements()

@dataclass
class PipelineResult:
    """Unified format for pipeline processing results"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Dict[str, Any]
    
    @classmethod
    def from_success(cls, data: Dict[str, Any], metadata: Dict[str, Any]) -> "PipelineResult":
        return cls(
            success=True,
            data=data,
            error=None,
            metadata=metadata
        )
    
    @classmethod
    def from_error(cls, error: str, metadata: Dict[str, Any]) -> "PipelineResult":
        return cls(
            success=False,
            data=None,
            error=error,
            metadata=metadata
        )

class ResultAdapter:
    """Adapter for pipeline results"""
    
    @staticmethod
    def adapt_pipeline_result(result: Any) -> PipelineResult:
        """Convert pipeline result to unified format"""
        if hasattr(result, "success") and hasattr(result, "data"):
            return PipelineResult(
                success=result.success,
                data=result.data if result.success else None,
                error=result.error if hasattr(result, "error") else None,
                metadata={
                    "source": "pipeline",
                    "timestamp": result.timestamp if hasattr(result, "timestamp") else None
                }
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

class ValidationAdapter:
    """Adapter for data validation"""
    
    @staticmethod
    def validate_query_result(result: AdaptedQueryResult) -> bool:
        """Validate adapted query result"""
        return all([
            isinstance(result.endpoint, str) and result.endpoint,
            isinstance(result.params, dict),
            isinstance(result.metadata, dict),
            isinstance(result.source_type, str)
        ])
    
    @staticmethod
    def validate_pipeline_result(result: PipelineResult) -> bool:
        """Validate pipeline result"""
        return all([
            isinstance(result.success, bool),
            result.data is None or isinstance(result.data, dict),
            result.error is None or isinstance(result.error, str),
            isinstance(result.metadata, dict)
        ])
```

```python:backend/app/pipeline/test_pipeline2.py
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
```


Let's run the updated test pipeline with the new adapters:

```bash
pip install httpx && python3 -m app.pipeline.test_pipeline2
```






We need to install pandas. Let's install it and run the test again:

```bash
pip install pandas && python3 -m app.pipeline.test_pipeline2
```


Great! The adapter implementation has been successful. Here's the analysis of the test results:

### Performance Metrics
1. **Adapter Performance**: 100% success (8/8)
   - All query results successfully adapted
   - No adapter failures

2. **Validation Performance**: 100% success (16/16)
   - All adapted results passed validation
   - Both query and pipeline results validated successfully

3. **API Fetch Performance**: 100% success (8/8)
   - All API requests completed successfully
   - Clean data retrieval from endpoints

4. **Data Processing**: 100% success (8/8)
   - All JSON responses successfully converted to DataFrames
   - No data transformation errors

### Key Improvements
1. **Type Safety**
   - Clean conversion between ProcessingResult and DataRequirements
   - Proper validation at each step

2. **Error Handling**
   - Graceful handling of API responses
   - Proper validation of data structures

3. **Data Flow**
   - Clear separation between processing stages
   - Consistent data format throughout pipeline

Would you like to:
1. Implement more complex test cases?
2. Add performance optimizations (caching, parallel processing)?
3. Enhance the adapter with more features?
4. Move forward with the full implementation?
