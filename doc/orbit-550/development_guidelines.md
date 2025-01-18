# Development Guidelines

## Code Organization

### Project Structure
```
backend/
├── app/
│   ├── main.py           # Main application entry
│   ├── pipeline/         # Data processing pipeline
│   │   ├── data2.py     # Core data processing
│   │   └── optimized_adapters.py
│   ├── query/           # Query processing
│   │   └── processor.py
│   └── analyst/         # Analysis generation
│       └── generate.py
└── tests/               # Test suites
```

### Module Responsibilities
1. **Pipeline**: Data fetching and processing
2. **Query**: Natural language processing
3. **Analyst**: Code generation and analysis
4. **Main**: API and orchestration

### Naming Conventions
- Files: lowercase with underscores
- Classes: PascalCase
- Functions: snake_case
- Constants: UPPERCASE_WITH_UNDERSCORES
- Type hints: Required for all functions

### Type Hints Usage
```python
from typing import Dict, List, Optional, Any

def process_data(
    data: Dict[str, Any],
    options: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Process data with optional configuration."""
    pass
```

## Testing Strategy

### Unit Tests
- Coverage target: 90%
- Test file naming: `test_*.py`
- Mock external dependencies
- Test each validation rule
- Test error cases

### Integration Tests
- Test complete data flow
- Test API endpoints
- Test error handling
- Performance benchmarks

### Test Data Management
```python
# Test data fixtures
@pytest.fixture
def sample_constructor_data():
    return {
        "constructorId": "ferrari",
        "year": 2023,
        "points": 400
    }
```

## Error Handling

### Error Categories
1. **Validation Errors**
   - Invalid data format
   - Missing required fields
   - Type mismatches

2. **Processing Errors**
   - Pipeline failures
   - Data transformation errors
   - Analysis generation errors

3. **System Errors**
   - API timeouts
   - Memory issues
   - Database errors

### Logging Standards
```python
# Logging levels
logger.debug("Detailed processing info")
logger.info("General progress")
logger.warning("Potential issues")
logger.error("Processing failures", exc_info=True)
```

### Debug Practices
1. Use detailed logging
2. Include context in errors
3. Track processing stages
4. Monitor performance metrics

## Data Processing

### Validation Rules
```python
def validate_constructor_data(data: Any) -> bool:
    """
    Validate constructor data format.
    
    Rules:
    1. Must be dict or list
    2. Required fields present
    3. Correct data types
    4. Valid value ranges
    """
    pass
```

### Normalization Standards
1. Consistent date formats
2. Standardized field names
3. Uniform data types
4. Handled missing values

### Performance Guidelines
1. Use vectorized operations
2. Implement caching
3. Batch processing
4. Memory management

### Memory Management
1. Clear unused DataFrames
2. Use generators for large datasets
3. Implement cleanup routines
4. Monitor memory usage

## Code Review Guidelines

### Review Checklist
1. Type hints complete
2. Error handling robust
3. Tests included
4. Documentation updated
5. Performance considered

### PR Requirements
1. Linked issue/ticket
2. Tests passing
3. Coverage maintained
4. Documentation updated
5. Clean commit history 