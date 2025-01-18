import pytest
import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any, Generator, TypedDict
import httpx
from datetime import datetime
import os
import psutil

from app.pipeline.data2 import DataPipeline, ProcessingError
from app.query.processor import QueryProcessor
from app.analyst.generate import DataAnalyzer
from app.main import create_app
from app.pipeline.optimized_adapters import OptimizedQueryAdapter
from app.exceptions import ValidationError
from app.validation import validate_constructor_data

# Type definitions
class DataRequirements(TypedDict):
    constructor: str
    years: List[int]
    constructors: List[str]

class PipelineResult(TypedDict):
    success: bool
    data: pd.DataFrame
    error: str | None

class AnalysisResult(TypedDict):
    success: bool
    results: Dict[str, Any]
    error: str | None

# Test Fixtures
@pytest.fixture
def sample_constructor_data() -> Dict[str, Any]:
    """Provide sample constructor data for tests."""
    return {
        "constructorId": "ferrari",
        "url": "http://example.com",
        "name": "Ferrari",
        "nationality": "Italian",
        "performance": {
            "points": 400,
            "position": 1,
            "wins": 5,
            "year": 2023
        }
    }

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Provide sample DataFrame for tests."""
    return pd.DataFrame([
        {"year": 2023, "constructor": "Ferrari", "points": 400},
        {"year": 2023, "constructor": "Mercedes", "points": 380}
    ])

@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "data": sample_constructor_data()}
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        yield mock_client

@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    class MockCache:
        async def get(self, key: str) -> Any:
            return None
        async def set(self, key: str, value: Any) -> None:
            pass
    return MockCache()

# Unit Tests
class TestQueryProcessing:
    @pytest.mark.asyncio
    async def test_basic_query_processing(self):
        """Test basic query processing functionality."""
        query = "Show Ferrari's performance from 2015 to 2023"
        processor = QueryProcessor()
        result = await processor.process_query(query)
        
        assert result.requirements is not None
        assert 'constructor' in result.requirements
        assert 'years' in result.requirements
        assert result.requirements['constructor'] == 'ferrari'
        assert len(result.requirements['years']) == 9  # 2015 to 2023

    @pytest.mark.asyncio
    async def test_complex_query_processing(self):
        """Test complex query with multiple constructors."""
        query = "Compare Ferrari and Mercedes performance in 2023"
        processor = QueryProcessor()
        result = await processor.process_query(query)
        
        assert 'constructors' in result.requirements
        assert len(result.requirements['constructors']) == 2
        assert 'ferrari' in result.requirements['constructors']
        assert 'mercedes' in result.requirements['constructors']

class TestDataValidation:
    def test_valid_constructor_data(self, sample_constructor_data):
        """Test validation of valid constructor data."""
        assert validate_constructor_data(sample_constructor_data) is True

    def test_invalid_constructor_data(self):
        """Test validation of invalid constructor data."""
        invalid_data = {"year": "invalid"}
        with pytest.raises(ValidationError) as exc_info:
            validate_constructor_data(invalid_data)
        assert "Invalid data format" in str(exc_info.value)

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        incomplete_data = {
            "constructorId": "ferrari",
            # Missing other required fields
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_constructor_data(incomplete_data)
        assert "Missing required fields" in str(exc_info.value)

class TestPipelineProcessing:
    @pytest.mark.asyncio
    async def test_pipeline_processing(self, mock_api_client, sample_constructor_data):
        """Test complete pipeline flow."""
        pipeline = DataPipeline()
        requirements = {
            "constructor": "ferrari",
            "years": [2023]
        }
        
        result = await pipeline.process(requirements)
        assert result.success is True
        assert isinstance(result.data, pd.DataFrame)
        assert not result.data.empty

    @pytest.mark.asyncio
    async def test_pipeline_data_transformation(self, sample_dataframe):
        """Test data transformation in pipeline."""
        pipeline = DataPipeline()
        transformed_df = await pipeline.transform_data(sample_dataframe)
        
        assert 'points_normalized' in transformed_df.columns
        assert 'performance_score' in transformed_df.columns
        assert transformed_df['points_normalized'].max() <= 1.0

# Integration Tests
class TestIntegration:
    @pytest.mark.asyncio
    async def test_complete_flow(self, mock_api_client):
        """Test end-to-end flow from query to result."""
        # Initialize components
        query_processor = QueryProcessor()
        pipeline = DataPipeline()
        analyzer = DataAnalyzer()
        
        # Process query
        query_result = await query_processor.process_query(
            "Compare Ferrari and Mercedes in 2023"
        )
        
        # Run pipeline
        pipeline_result = await pipeline.process(query_result.requirements)
        
        # Generate analysis
        analysis = await analyzer.analyze(pipeline_result.data)
        
        assert analysis.success is True
        assert 'comparison' in analysis.results
        assert len(analysis.results['comparison']) > 0

    @pytest.mark.asyncio
    async def test_api_endpoints(self, test_app):
        """Test API endpoints with various queries."""
        async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/analyze",
                json={"query": "Show Ferrari's wins in 2023"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'data' in data
            assert 'executed_code' in data

# Performance Tests
class TestPerformance:
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_app):
        """Test system under concurrent load."""
        async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
            tasks = []
            start_time = datetime.now()
            
            for _ in range(100):
                task = asyncio.create_task(
                    client.post(
                        "/api/v1/analyze",
                        json={"query": "Show Ferrari's performance"}
                    )
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = datetime.now()
            
            # Verify results
            assert all(r.status_code == 200 for r in results)
            
            # Check performance
            total_time = (end_time - start_time).total_seconds()
            assert total_time < 20  # Less than 20 seconds for 100 requests

    @pytest.mark.performance
    def test_memory_optimization(self, sample_dataframe):
        """Test memory usage during processing."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        df = process_large_dataset(sample_dataframe)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        cleanup_processing(df)
        assert memory_increase < 512  # Less than 512MB increase

# Error Handling Tests
class TestErrorHandling:
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        invalid_data = {"invalid": "data"}
        
        with pytest.raises(ValidationError) as exc_info:
            validate_constructor_data(invalid_data)
        
        assert "Invalid data format" in str(exc_info.value)
        assert exc_info.value.error_code == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test system recovery from errors."""
        with patch('app.pipeline.data2.DataPipeline.process') as mock_process:
            mock_process.side_effect = ProcessingError("Pipeline failed")
            
            result = await process_with_recovery(mock_process)
            assert result.success is True  # Should recover
            assert result.used_fallback is True
            assert result.error_details == "Pipeline failed"

    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_app):
        """Test rate limiting functionality."""
        async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
            # Make requests at rate higher than limit
            responses = []
            for _ in range(150):  # Exceed rate limit
                response = await client.post(
                    "/api/v1/analyze",
                    json={"query": "Show Ferrari's performance"}
                )
                responses.append(response)
            
            # Verify rate limiting
            rate_limited = any(r.status_code == 429 for r in responses)
            assert rate_limited

# Helper Functions
def process_large_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Process a large dataset for memory testing."""
    # Simulate large data processing
    large_df = pd.concat([df] * 1000, ignore_index=True)
    return large_df.copy()

def cleanup_processing(df: pd.DataFrame) -> None:
    """Cleanup after processing."""
    del df
    import gc
    gc.collect()

async def process_with_recovery(process_func: Any) -> Dict[str, Any]:
    """Process with error recovery."""
    try:
        return await process_func()
    except ProcessingError as e:
        return {
            "success": True,
            "used_fallback": True,
            "error_details": str(e),
            "data": {"fallback": "data"}
        }

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=term-missing"]) 