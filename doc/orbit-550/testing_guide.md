# Testing Guide

## Test Structure

### 1. Unit Tests

#### Query Processing Tests
```python
@pytest.mark.asyncio
async def test_query_processing():
    """Test query processing and adaptation."""
    # Test natural language query processing
    query = "Show Ferrari's performance from 2015 to 2023"
    processor = QueryProcessor()
    result = await processor.process_query(query)
    
    assert result.requirements is not None
    assert 'constructor' in result.requirements
    assert 'years' in result.requirements
```

#### Data Validation Tests
```python
def test_constructor_data_validation():
    """Test constructor data validation rules."""
    # Test valid data
    valid_data = {
        "constructorId": "ferrari",
        "year": 2023,
        "points": 400
    }
    assert validate_constructor_data(valid_data) is True
    
    # Test invalid data
    invalid_data = {"year": "invalid"}
    with pytest.raises(ValidationError):
        validate_constructor_data(invalid_data)
```

#### Pipeline Processing Tests
```python
@pytest.mark.asyncio
async def test_pipeline_processing():
    """Test complete pipeline flow."""
    pipeline = DataPipeline()
    requirements = DataRequirements(
        constructor="ferrari",
        years=[2023]
    )
    
    result = await pipeline.process(requirements)
    assert result.success is True
    assert isinstance(result.data, pd.DataFrame)
```

### 2. Integration Tests

#### Full Flow Tests
```python
@pytest.mark.asyncio
async def test_complete_flow():
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
```

#### API Endpoint Tests
```python
@pytest.mark.asyncio
async def test_api_endpoints():
    """Test API endpoints with various queries."""
    async with TestClient(app) as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"query": "Show Ferrari's wins in 2023"}
        )
        
        assert response.status_code == 200
        assert response.json()['success'] is True
```

### 3. Performance Tests

#### Load Testing
```python
@pytest.mark.performance
async def test_concurrent_requests():
    """Test system under concurrent load."""
    async with TestClient(app) as client:
        tasks = []
        for _ in range(100):
            task = asyncio.create_task(
                client.post(
                    "/api/v1/analyze",
                    json={"query": "Show Ferrari's performance"}
                )
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        assert all(r.status_code == 200 for r in results)
```

#### Memory Usage Tests
```python
@pytest.mark.performance
def test_memory_optimization():
    """Test memory usage during processing."""
    initial_memory = get_memory_usage()
    
    # Process large dataset
    df = process_large_dataset()
    
    final_memory = get_memory_usage()
    cleanup_processing(df)
    
    assert (final_memory - initial_memory) < MEMORY_THRESHOLD
```

### 4. Error Handling Tests

#### Validation Error Tests
```python
def test_validation_error_handling():
    """Test handling of validation errors."""
    invalid_data = {"invalid": "data"}
    
    with pytest.raises(ValidationError) as exc_info:
        validate_constructor_data(invalid_data)
    
    assert "Invalid data format" in str(exc_info.value)
    assert exc_info.value.error_code == "VALIDATION_ERROR"
```

#### Recovery Tests
```python
@pytest.mark.asyncio
async def test_error_recovery():
    """Test system recovery from errors."""
    # Simulate pipeline failure
    with patch('pipeline.process') as mock_process:
        mock_process.side_effect = ProcessingError("Pipeline failed")
        
        result = await process_with_recovery(mock_process)
        assert result.success is True  # Should recover
        assert result.used_fallback is True
```

## Test Fixtures

### 1. Data Fixtures
```python
@pytest.fixture
def sample_constructor_data():
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
def sample_dataframe():
    """Provide sample DataFrame for tests."""
    return pd.DataFrame([
        {"year": 2023, "constructor": "Ferrari", "points": 400},
        {"year": 2023, "constructor": "Mercedes", "points": 380}
    ])
```

### 2. Mock Fixtures
```python
@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = \
            MockResponse({"success": True})
        yield mock_client

@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    return MockCache()
```

## Test Configuration

### 1. pytest Configuration
```ini
# pytest.ini
[pytest]
markers =
    asyncio: mark test as async
    performance: mark test as performance test
    integration: mark test as integration test
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 2. Test Environment
```python
# conftest.py
import pytest
import asyncio
from typing import Generator

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_app():
    """Provide test application instance."""
    from app.main import create_app
    return create_app(testing=True)
```

## Running Tests

### 1. Test Commands
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest -m performance

# Run with coverage
pytest --cov=app tests/
```

### 2. CI/CD Integration
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest --cov=app tests/
          coverage report
```

## Test Coverage Requirements

### 1. Coverage Targets
- Unit Tests: 90% coverage
- Integration Tests: 80% coverage
- Critical Paths: 100% coverage

### 2. Critical Paths
1. Query Processing Flow
2. Data Validation
3. Pipeline Processing
4. Error Recovery
5. API Endpoints

### 3. Coverage Reporting
```bash
# Generate coverage report
coverage run -m pytest
coverage report
coverage html  # Generate HTML report
```

## Performance Benchmarks

### 1. Response Time Targets
- API Endpoints: < 2 seconds
- Query Processing: < 500ms
- Pipeline Processing: < 1.5 seconds

### 2. Memory Usage Targets
- Peak Memory: < 512MB
- Memory Leak: None after cleanup
- Cache Size: < 200MB

### 3. Concurrent Load Targets
- Concurrent Users: 100
- Response Time Degradation: < 20%
- Error Rate: < 0.1% 