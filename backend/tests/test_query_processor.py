"""Comprehensive test suite for the Query Processor component."""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import json
import logging
from app.query.processor import QueryProcessor
from app.query.models import DataRequirements
from tests.test_queries import TestQueries

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryProcessorMetrics:
    """Tracks metrics for query processor testing."""
    
    def __init__(self):
        self.total_queries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.total_processing_time = 0
        self.errors: Dict[str, int] = {}
        self.endpoint_usage: Dict[str, int] = {}
        self.results: List[Dict[str, Any]] = []
        
    def record_success(self, query: str, result: Dict[str, Any], processing_time: float):
        """Record a successful query processing."""
        self.successful_queries += 1
        self.total_queries += 1
        self.total_processing_time += processing_time
        
        endpoint = result.get('endpoint', 'unknown')
        self.endpoint_usage[endpoint] = self.endpoint_usage.get(endpoint, 0) + 1
        
        self.results.append({
            'query': query,
            'success': True,
            'result': result,
            'processing_time': processing_time
        })
        
    def record_failure(self, query: str, error: str):
        """Record a failed query processing."""
        self.failed_queries += 1
        self.total_queries += 1
        
        self.errors[error] = self.errors.get(error, 0) + 1
        
        self.results.append({
            'query': query,
            'success': False,
            'error': error
        })
        
    def get_success_rate(self) -> float:
        """Calculate the success rate."""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100
        
    def get_average_processing_time(self) -> float:
        """Calculate average processing time for successful queries."""
        if self.successful_queries == 0:
            return 0.0
        return self.total_processing_time / self.successful_queries
        
    def save_results(self, category: str):
        """Save test results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'query_processor_results_{category}_{timestamp}.json'
        
        report = {
            'summary': {
                'total_queries': self.total_queries,
                'successful_queries': self.successful_queries,
                'failed_queries': self.failed_queries,
                'success_rate': self.get_success_rate(),
                'average_processing_time': self.get_average_processing_time(),
                'endpoint_usage': self.endpoint_usage,
                'error_types': self.errors
            },
            'detailed_results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Results saved to {filename}")

def validate_requirements(requirements: DataRequirements) -> bool:
    """Validate the generated requirements format."""
    if not requirements.endpoint:
        return False
        
    # Validate endpoint format
    if not requirements.endpoint.startswith('/api/f1/'):
        return False
        
    # Validate params
    if not isinstance(requirements.params, dict):
        return False
        
    # Check for required parameters based on endpoint
    if 'drivers' in requirements.endpoint:
        if 'driver' not in requirements.params and 'season' not in requirements.params:
            return False
    elif 'constructors' in requirements.endpoint:
        if 'constructor' not in requirements.params and 'season' not in requirements.params:
            return False
            
    return True

@pytest.mark.asyncio
async def test_query_category(category_name: str) -> QueryProcessorMetrics:
    """Test query processor on a specific category of queries."""
    processor = QueryProcessor()
    metrics = QueryProcessorMetrics()
    
    # Get queries for the category
    try:
        queries = TestQueries.get_queries_by_category(category_name)
    except ValueError as e:
        logger.error(f"Failed to get queries: {e}")
        return metrics
    
    logger.info(f"Testing {len(queries)} queries from category: {category_name}")
    
    for query in queries:
        try:
            start_time = datetime.now().timestamp()
            result = await processor.process_query(query)
            processing_time = datetime.now().timestamp() - start_time
            
            # Validate requirements
            if not result or not result.requirements or not validate_requirements(result.requirements):
                metrics.record_failure(query, "Invalid requirements format")
                continue
            
            # Record success
            metrics.record_success(
                query=query,
                result={
                    'endpoint': result.requirements.endpoint,
                    'parameters': result.requirements.params,
                    'confidence': result.confidence,
                    'source': result.source
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            metrics.record_failure(query, str(e))
            logger.error(f"Error processing query '{query}': {e}")
    
    # Save results
    metrics.save_results(category_name)
    return metrics

@pytest.mark.asyncio
async def test_basic_stats():
    """Test query processor on basic statistics queries."""
    metrics = await test_query_category("Natural Language to Stats")
    
    # Assert success criteria
    assert metrics.get_success_rate() >= 90.0, "Basic stats queries success rate below 90%"
    assert metrics.get_average_processing_time() < 5.0, "Average processing time above 5 seconds"
    
    return metrics

@pytest.mark.asyncio
async def test_driver_comparisons():
    """Test query processor on driver comparison queries."""
    metrics = await test_query_category("Driver Comparisons")
    
    # Assert success criteria
    assert metrics.get_success_rate() >= 90.0, "Driver comparison queries success rate below 90%"
    assert metrics.get_average_processing_time() < 5.0, "Average processing time above 5 seconds"
    
    return metrics

@pytest.mark.asyncio
async def test_historical_trends():
    """Test query processor on historical trend queries."""
    metrics = await test_query_category("Historical Trends")
    
    # Assert success criteria
    assert metrics.get_success_rate() >= 90.0, "Historical trends queries success rate below 90%"
    assert metrics.get_average_processing_time() < 5.0, "Average processing time above 5 seconds"
    
    return metrics

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_basic_stats())
    asyncio.run(test_driver_comparisons())
    asyncio.run(test_historical_trends()) 