# Troubleshooting Guide

## Common Issues

### 1. Data Processing Issues

#### Inconsistent DataFrame Lengths
**Symptoms**:
- Different row counts between years
- Missing data for some seasons
- Duplicate entries

**Causes**:
- Inconsistent API responses
- Failed data fetches
- Duplicate data in pipeline

**Solutions**:
```python
# Check DataFrame shape after each transformation
logger.debug(f"Shape after cleaning: {df.shape}")
logger.debug(f"Shape after normalization: {df.shape}")

# Validate row counts
assert len(df) == len(df['year'].unique()), "Duplicate years found"
```

#### Constructor Data Format Issues
**Symptoms**:
- Unhashable type errors
- JSON parsing failures
- Missing constructor information

**Causes**:
- Mixed data types in ConstructorTable
- Invalid JSON strings
- Incomplete API responses

**Solutions**:
```python
# Validate constructor data format
if not isinstance(data, (list, dict)):
    logger.error(f"Invalid data type: {type(data)}")
    return default_empty_data()

# Handle string-encoded data
if isinstance(data, str):
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON data")
        return default_empty_data()
```

### 2. API Integration Issues

#### Response Handling
**Symptoms**:
- Timeout errors
- Incomplete responses
- Rate limiting errors

**Solutions**:
```python
# Implement retry logic
@retry(max_attempts=3, backoff=2)
async def fetch_with_retry(url: str) -> Dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"API fetch failed: {e}")
        raise
```

#### Error Recovery
**Symptoms**:
- Failed batch processing
- Partial data returns
- Pipeline interruptions

**Solutions**:
```python
# Implement graceful degradation
try:
    result = await process_full_pipeline(data)
except Exception as e:
    logger.warning(f"Full pipeline failed: {e}")
    result = await process_basic_pipeline(data)
```

### 3. Performance Issues

#### Slow Response Times
**Symptoms**:
- High latency
- Timeout errors
- Memory usage spikes

**Solutions**:
```python
# Implement caching
cache_key = f"{endpoint}:{params_hash}"
if result := await cache.get(cache_key):
    return result

# Optimize memory usage
def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage."""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.Categorical(df[col])
    return df
```

## Debugging Practices

### 1. Logging Levels
```python
# Debug level for detailed processing
logger.debug("Processing stage details", extra={
    'shape': df.shape,
    'columns': df.columns,
    'dtypes': df.dtypes
})

# Info level for progress
logger.info("Processing completed", extra={
    'time_taken': time.time() - start_time,
    'rows_processed': len(df)
})

# Error level for failures
logger.error("Processing failed", exc_info=True, extra={
    'stage': current_stage,
    'input_shape': input_shape
})
```

### 2. Debug Points
Key points to add logging:
1. After data fetching
2. After validation
3. After cleaning
4. After normalization
5. Before analysis

### 3. Data Inspection
```python
# Inspect DataFrame at key points
def inspect_dataframe(df: pd.DataFrame, stage: str) -> None:
    """Log DataFrame details at each stage."""
    logger.debug(f"Stage: {stage}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {df.columns}")
    logger.debug(f"Data types: {df.dtypes}")
    logger.debug(f"Sample: {df.head(1)}")
```

## Recovery Procedures

### 1. Data Recovery
```python
# Implement data recovery
async def recover_data(failed_years: List[str]) -> pd.DataFrame:
    """Recover data for failed years."""
    recovered_data = []
    for year in failed_years:
        try:
            data = await fetch_with_retry(year)
            recovered_data.append(data)
        except Exception as e:
            logger.error(f"Recovery failed for {year}: {e}")
    return pd.DataFrame(recovered_data)
```

### 2. Error Recovery
```python
# Implement error recovery
def recover_from_error(e: Exception, df: pd.DataFrame) -> pd.DataFrame:
    """Recover from processing errors."""
    if isinstance(e, ValidationError):
        return handle_validation_error(df)
    elif isinstance(e, ProcessingError):
        return handle_processing_error(df)
    return df
```

### 3. System Recovery
```python
# Implement system recovery
async def recover_system_state():
    """Recover system state after failure."""
    await clear_cache()
    await reset_connections()
    await check_system_health()
``` 