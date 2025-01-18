# P2 Pipeline Setup Guide

## Directory Structure
```
backend/
├── app/
│   ├── pipeline/             # Pipeline System
│   │   ├── __init__.py
│   │   ├── data2.py         # Enhanced data processing
│   │   ├── optimized_adapters.py  # Optimized adapters
│   │   ├── test_pipeline2.py      # Test suite
│   │   └── test_endpoints.py      # Endpoint tests
│   ├── query/               # Query Processing
│   │   ├── __init__.py
│   │   ├── processor.py     # Query processor
│   │   ├── models.py        # Data models
│   │   └── test_queries.py  # Query tests
│   └── main.py             # FastAPI application
├── tests/                  # Test suites
└── requirements.txt        # Python dependencies
```

## Installation

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies
```python
# requirements.txt
httpx==0.28.1
pandas==2.2.3
fastapi==0.109.0
asyncio==3.4.3
pytest==7.4.4
pytest-asyncio==0.23.5
```

## Configuration

### 1. Pipeline Configuration
```python
# config/pipeline.py
PIPELINE_CONFIG = {
    'batch_size': 4,
    'max_retries': 3,
    'retry_delay': 1.0,
    'timeout': 30.0
}

CACHE_CONFIG = {
    'max_size': 1000,
    'ttl': 3600,
    'cleanup_interval': 300
}
```

### 2. API Configuration
```python
# config/api.py
API_CONFIG = {
    'base_url': 'http://ergast.com/api/f1',
    'rate_limit': 100,  # requests per minute
    'connection_pool': 20
}
```

## Core Components

### 1. Data Pipeline
```python
# app/pipeline/data2.py
class DataPipeline:
    """Enhanced data processing pipeline"""
    def __init__(self):
        self.cache_manager = CacheManager()
        self.parallel_manager = ParallelFetchManager()
    
    async def process(self, requirements: Any) -> Dict[str, Any]:
        """Process data requirements"""
        # Implementation details in data2.py
```

### 2. Optimized Adapters
```python
# app/pipeline/optimized_adapters.py
class OptimizedQueryAdapter:
    """Enhanced query adapter"""
    def __init__(self):
        self.cache_manager = CacheManager()
        self.parallel_processor = ParallelProcessor()
    
    async def adapt(self, result: Any) -> OptimizedQueryResult:
        """Adapt query result"""
        # Implementation details in optimized_adapters.py
```

## Testing

### 1. Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test suite
python -m pytest backend/app/pipeline/test_pipeline2.py

# Run with coverage
python -m pytest --cov=app tests/
```

### 2. Test Configuration
```python
# tests/conftest.py
@pytest.fixture
def test_client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def pipeline():
    """Create pipeline instance"""
    return DataPipeline()
```

## Usage Examples

### 1. Basic Query Processing
```python
from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor

async def process_query(query: str):
    # Initialize components
    processor = QueryProcessor()
    pipeline = DataPipeline()
    
    # Process query
    query_result = await processor.process_query(query)
    result = await pipeline.process(query_result)
    return result
```

### 2. Parallel Processing
```python
from app.pipeline.optimized_adapters import ParallelFetchManager

async def process_multi_entity(entities: List[str]):
    # Initialize manager
    fetch_manager = ParallelFetchManager()
    
    # Create requests
    requests = [
        ParallelFetchRequest(
            endpoint="/api/f1/drivers",
            params={"driver": entity},
            entity_type="driver",
            entity_id=entity
        )
        for entity in entities
    ]
    
    # Fetch data
    results = await fetch_manager.fetch_all(requests)
    return results
```

## Monitoring

### 1. Performance Metrics
```python
from app.monitoring import MetricsCollector

metrics = MetricsCollector()
metrics.record_processing_time(time)
metrics.record_cache_hit()
metrics.print_summary()
```

### 2. Error Tracking
```python
from app.monitoring import ErrorTracker

error_tracker = ErrorTracker()
error_tracker.record_error(error, context)
error_tracker.generate_report()
```

## Troubleshooting

### 1. Common Issues
```python
# Cache issues
- Clear cache: await cache_manager.clear()
- Reset cache: await cache_manager.reset()
- Check cache size: print(len(cache_manager.cache))

# Connection issues
- Check API status
- Verify rate limits
- Test connection pool
```

### 2. Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug flag
python -m app.pipeline.test_pipeline2 --debug
```

## Security

### 1. API Authentication
```python
# Set up API key
API_KEY = os.environ.get('F1_API_KEY')

# Configure client
client = httpx.AsyncClient(
    headers={'Authorization': f'Bearer {API_KEY}'},
    timeout=30.0
)
```

### 2. Rate Limiting
```python
from app.security import RateLimiter

limiter = RateLimiter(max_rate=100)
async with limiter:
    result = await fetch_data()
```

## Deployment

### 1. Production Setup
```bash
# Set environment
export ENV=production

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "cache": await cache_manager.health_check(),
        "pipeline": await pipeline.health_check()
    }
```

Would you like to:
1. Add more usage examples?
2. Include advanced configuration options?
3. Add deployment strategies?
4. Expand troubleshooting guides? 