"""
Batch testing module for running concurrent query tests against the main.py application.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    import httpx
except ImportError:
    print("httpx not found. Please install it with: pip install httpx")
    raise

import pandas as pd

from .metrics import PerformanceMetrics
from .storage import TestArtifactStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryStageResult:
    """Represents the result of a single query stage execution."""
    def __init__(self, query: str, stage: str):
        self.query = query
        self.stage = stage
        self.start_time: float = 0
        self.end_time: float = 0
        self.success: bool = False
        self.error: Optional[str] = None
        self.response_data: Optional[Dict] = None

    @property
    def duration(self) -> float:
        """Return the duration of the stage execution in seconds."""
        return self.end_time - self.start_time

    def to_dict(self) -> Dict:
        """Convert the stage result to a dictionary."""
        return {
            "query": self.query,
            "stage": self.stage,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "response_data": self.response_data
        }

class TestResult:
    """Represents the complete result of a test run for a single query."""
    def __init__(self, query: str):
        self.query = query
        self.stages: List[QueryStageResult] = []
        self.overall_success: bool = False
        self.start_time: float = 0
        self.end_time: float = 0

    @property
    def duration(self) -> float:
        """Return the total duration of all stages."""
        return self.end_time - self.start_time

    def add_stage(self, stage: QueryStageResult):
        """Add a stage result to this test."""
        self.stages.append(stage)

    def to_dict(self) -> Dict:
        """Convert the test result to a dictionary."""
        return {
            "query": self.query,
            "overall_success": self.overall_success,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "stages": [stage.to_dict() for stage in self.stages]
        }

class BatchTestRunner:
    """Main class for running batch tests with concurrent queries."""
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.metrics = PerformanceMetrics()
        self.storage = TestArtifactStorage()
        self.query_sets: Dict[str, List[str]] = {}
        self.active_tests: Set[str] = set()
        self.results: List[TestResult] = []

    async def load_query_sets(self):
        """Load available query sets from the eval directory."""
        eval_dir = Path("backend/eval")
        for file in eval_dir.glob("query_test_*.txt"):
            queries = []
            with open(file) as f:
                current_category = None
                for line in f:
                    line = line.strip()
                    if line.startswith("#"):
                        current_category = line[1:].strip()
                    elif line and not line.startswith("//"):
                        queries.append(line)
            self.query_sets[file.stem] = queries
            logger.info(f"Loaded {len(queries)} queries from {file.name}")

    async def process_query(self, query: str) -> TestResult:
        """Process a single query through all testing stages."""
        result = TestResult(query)
        result.start_time = self.metrics.current_time()
        
        try:
            # Stage 1: Initial query processing
            stage = QueryStageResult(query, "initial_processing")
            stage.start_time = self.metrics.current_time()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/query",
                    json={"query": query}
                )
                stage.response_data = response.json()
                stage.success = response.status_code == 200
                
            stage.end_time = self.metrics.current_time()
            result.add_stage(stage)

            # Add more stages as needed...
            
            result.overall_success = all(stage.success for stage in result.stages)
            
        except Exception as e:
            logger.error(f"Error processing query: {query}", exc_info=True)
            result.overall_success = False
            
        result.end_time = self.metrics.current_time()
        return result

    async def run_batch(self, query_set_name: str, concurrency: int = 3):
        """Run a batch of tests with the specified concurrency level."""
        if query_set_name not in self.query_sets:
            raise ValueError(f"Query set '{query_set_name}' not found")

        queries = self.query_sets[query_set_name]
        logger.info(f"Starting batch test with {len(queries)} queries (concurrency: {concurrency})")
        
        self.metrics.start_batch()
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_process(query: str):
            async with semaphore:
                return await self.process_query(query)

        tasks = [bounded_process(query) for query in queries]
        self.results = await asyncio.gather(*tasks)
        
        self.metrics.end_batch()
        await self.storage.store_results(self.results, query_set_name)
        
        return self.results

    def print_summary(self):
        """Print a summary of the test results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.overall_success)
        
        print("\nTest Summary:")
        print(f"Total Queries: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {(successful/total)*100:.2f}%")
        print(f"Total Duration: {sum(r.duration for r in self.results):.2f}s")
        
        self.metrics.print_summary()

async def main():
    """Main entry point for running batch tests."""
    runner = BatchTestRunner()
    await runner.load_query_sets()
    
    # List available query sets
    print("\nAvailable Query Sets:")
    for name in runner.query_sets:
        print(f"- {name} ({len(runner.query_sets[name])} queries)")
    
    # Allow user to select query set
    query_set = input("\nEnter query set name: ").strip()
    concurrency = int(input("Enter concurrency level (default: 3): ") or "3")
    
    # Run tests
    results = await runner.run_batch(query_set, concurrency)
    runner.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 