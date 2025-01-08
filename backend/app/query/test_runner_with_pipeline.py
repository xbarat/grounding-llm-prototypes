"""Test runner combining Q2 query processing with optimized pipeline"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from .processor import QueryProcessor
from ..pipeline.data2 import DataPipeline
from ..pipeline.optimized_adapters import (
    OptimizedQueryAdapter,
    OptimizedResultAdapter,
    OptimizedValidationAdapter
)

class TestMetricsCollector:
    def __init__(self):
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.query_types = defaultdict(lambda: {"total": 0, "success": 0, "failure": 0})
        self.processing_times = []
        self.error_types = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_query(self, query: str, success: bool, time: float, error: Optional[str] = None):
        self.total_queries += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
            if error:
                self.error_types[str(error)] += 1
        self.processing_times.append(time)
        
        # Categorize query
        query_type = self._categorize_query(query)
        self.query_types[query_type]["total"] += 1
        if success:
            self.query_types[query_type]["success"] += 1
        else:
            self.query_types[query_type]["failure"] += 1
    
    def _categorize_query(self, query: str) -> str:
        query = query.lower()
        if "compare" in query or "vs" in query or "versus" in query:
            return "comparison"
        if "how many" in query or "what is" in query or "what's" in query:
            return "stats"
        if "since" in query or "from" in query or "over" in query:
            return "historical"
        if "qualifying" in query or "pole" in query:
            return "qualifying"
        if "race" in query or "podium" in query or "win" in query:
            return "race"
        return "other"
    
    def get_summary(self) -> Dict[str, Any]:
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        success_rate = (self.successful_queries / self.total_queries * 100) if self.total_queries else 0
        
        return {
            "total_queries": self.total_queries,
            "success_rate": f"{success_rate:.1f}%",
            "average_processing_time": f"{avg_time:.2f}s",
            "query_type_performance": {
                qtype: {
                    "total": stats["total"],
                    "success_rate": f"{(stats['success'] / stats['total'] * 100):.1f}%" if stats['total'] > 0 else "0%"
                }
                for qtype, stats in self.query_types.items()
            },
            "error_distribution": dict(self.error_types),
            "cache_performance": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": f"{(self.cache_hits / (self.cache_hits + self.cache_misses) * 100):.1f}%" if (self.cache_hits + self.cache_misses) > 0 else "0%"
            }
        }

async def run_pipeline_tests(queries: List[str]) -> Dict[str, Any]:
    """Run tests through the complete pipeline"""
    processor = QueryProcessor()
    pipeline = DataPipeline()
    query_adapter = OptimizedQueryAdapter()
    result_adapter = OptimizedResultAdapter()
    validation_adapter = OptimizedValidationAdapter()
    metrics = TestMetricsCollector()
    
    for query in queries:
        start_time = datetime.now().timestamp()
        try:
            # Process query
            query_result = await processor.process_query(query)
            
            # Adapt query result
            adapted_query = await query_adapter.adapt(query_result)
            if adapted_query.cache_hit:
                metrics.cache_hits += 1
            else:
                metrics.cache_misses += 1
            
            # Process through pipeline
            requirements = adapted_query.to_data_requirements()
            pipeline_response = await pipeline.process(requirements)
            
            # Adapt pipeline result
            pipeline_result = await result_adapter.adapt_pipeline_result(pipeline_response, start_time)
            
            # Record metrics
            processing_time = datetime.now().timestamp() - start_time
            success = pipeline_result.success and pipeline_result.data is not None
            metrics.record_query(query, success, processing_time, pipeline_result.error)
            
        except Exception as e:
            processing_time = datetime.now().timestamp() - start_time
            metrics.record_query(query, False, processing_time, str(e))
    
    return metrics.get_summary()

async def main():
    test_queries = [
        # Natural Language to Stats
        "Who won the most races in 2023?",
        "What is the fastest lap time recorded in 2023?",
        "Which team has the most podium finishes this season?",
        "How many races has Verstappen won in 2023?",
        "What is the average lap time for Hamilton in 2023?",
        "Which driver has the highest pole position percentage in 2023?",
        "How many races were won by Ferrari in 2022?",
        "Who leads the driver standings in 2023?",
        
        # Driver Comparisons
        "Compare Verstappen and Hamilton's wins in 2023",
        "Who has more podium finishes: Leclerc or Norris in 2023?",
        "Compare lap times between Verstappen and Alonso in Monaco 2023",
        "Which driver performed better in the rain: Verstappen or Russell?",
        "How does Verstappen's pole position percentage compare to Hamilton's in 2023?",
        "Compare Verstappen and Hamilton in terms of race wins and fastest laps",
        "Who had the better average qualifying position: Norris or Sainz?",
        "Compare Leclerc and Perez's DNFs in 2023",
        
        # Historical Trends
        "How has Ferrari's win rate changed since 2015?",
        "What are Red Bull's podium finishes from 2010 to 2023?",
        "Which driver has the most wins in wet races since 2000?",
        "How many wins does Hamilton have each season since 2014?",
        "Which team dominated constructors' championships from 2010 to 2020?",
        "Show Mercedes' win percentage over the last decade",
        "How have the fastest lap times changed in Monaco since 2010?",
        "What is the historical win trend of Verstappen?"
    ]
    
    results = await run_pipeline_tests(test_queries)
    print("\nTest Results Summary:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 