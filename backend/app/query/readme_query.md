# Query Module Documentation

## Overview
The Query module is responsible for converting natural language F1 queries into structured API requirements. It serves as Stage 1 of the F1 data pipeline.

## Core Components

### 1. Query Processor (`processor.py`)
Main component for query processing and requirement generation.

```python
class QueryProcessor:
    async def process_query(query: str) -> QueryResult:
        """Converts natural language query to API requirements"""
```

Key Features:
- Natural language understanding
- API endpoint determination
- Parameter extraction
- Confidence scoring
- Error handling

### 2. Data Models (`models.py`)
Core data structures for query processing.

```python
class DataRequirements:
    endpoint: str          # F1 API endpoint
    params: Dict[str, Any] # Query parameters
    source: str           # Data source type

class QueryResult:
    requirements: DataRequirements
    confidence: float
    processing_time: float
```

### 3. GPT-4 Assistant Integration (`q2_assistants.py`)
Handles interaction with GPT-4 for query analysis.

Key Features:
- Query intent classification
- Entity extraction
- Parameter validation
- Context management

## Supported Query Types

1. **Basic Statistics**
   ```python
   # Example: "Who won the most races in 2023?"
   {
     "endpoint": "/api/f1/races",
     "params": {"season": "2023"}
   }
   ```

2. **Driver Comparisons**
   ```python
   # Example: "Compare Verstappen and Hamilton's wins in 2023"
   {
     "endpoint": "/api/f1/drivers",
     "params": {
       "season": "2023",
       "driver": ["max_verstappen", "lewis_hamilton"]
     }
   }
   ```

3. **Historical Trends**
   ```python
   # Example: "How has Ferrari's win rate changed since 2015?"
   {
     "endpoint": "/api/f1/constructors",
     "params": {
       "season": ["2015"..."2023"],
       "constructor": "ferrari"
     }
   }
   ```

## Performance Characteristics

- Average Processing Time:
  - Basic Queries: ~5.11s
  - Comparison Queries: ~5.39s
  - Historical Queries: ~8.03s

- Success Rates:
  - Query Processing: >90%
  - Parameter Extraction: >95%
  - Endpoint Mapping: >98%

## Error Handling

1. **Input Validation**
   - Malformed queries
   - Missing required parameters
   - Invalid date ranges

2. **API Constraints**
   - Rate limiting
   - Timeout handling
   - Invalid endpoint combinations

3. **Processing Errors**
   - GPT-4 API failures
   - Parameter extraction failures
   - Confidence threshold failures

## Usage Example

```python
from app.query.processor import QueryProcessor
from app.query.models import QueryResult

async def process_f1_query(query: str) -> QueryResult:
    processor = QueryProcessor()
    result = await processor.process_query(query)
    
    if result.confidence < 0.8:
        raise ValueError("Low confidence in query understanding")
        
    return result
```

## Integration Points

1. **Upstream**
   - FastAPI endpoints
   - Web interface
   - CLI tools

2. **Downstream**
   - F1 API client
   - Data pipeline
   - Analysis engine

## Testing

```bash
# Run query processor tests
pytest tests/test_query_processor.py -v --cov=app.query

# Test specific query category
pytest tests/test_query_processor.py::test_basic_stats -v
```

## Dependencies
- OpenAI GPT-4
- Python 3.8+
- pytest for testing
- FastAPI for API integration 