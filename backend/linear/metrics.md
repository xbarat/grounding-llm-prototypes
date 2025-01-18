# Pipeline Performance Metrics

## Standard 24-Query Test Results
Performance metrics from running the standard test suite with 24 queries:

### Core Metrics
- **Total Queries**: 24
- **Average Processing Time**: 6.81 seconds
- **Success Rate**: 91.7% (22/24 queries)

### Component Performance
- **Adapter Performance**: 100% success (24/24)
- **Validation Performance**: 100% success (48/48)
- **Query → JSON (API Fetch)**: 91.7% success (22/24)
- **JSON → DataFrame**: 100% success (22/22)

### Cache Performance
- **Cache Hits**: 0% (0/48)
- **Cache Misses**: 100% (48/48)
- **Note**: First run baseline, cache was empty

## Tough Query Test Results (Historical & Ambiguous)
Performance metrics from running complex historical and ambiguous queries:

### Core Metrics
- **Total Queries**: 20 (10 historical, 10 ambiguous)
- **Average Processing Time**: 6.95 seconds
- **Overall Success Rate**: 85% (17/20 queries)

### Query Type Performance
- **Historical Queries**: 100% success (10/10)
- **Ambiguous Queries**: 70% success (7/10)
- **Entity Resolution**: 100% success when detected (1/1)

### Component Performance
- **Adapter Performance**: 100% success (20/20)
- **Validation Performance**: 100% success (40/40)
- **Query → JSON (API Fetch)**: 85% success (17/20)
- **JSON → DataFrame**: 100% success (17/17)

### Cache Performance
- **Cache Hits**: 0% (0/40)
- **Cache Misses**: 100% (40/40)
- **Note**: First run baseline, cache was empty

## Failure Analysis

### Standard Test Failures
- **Failed Queries**: 2/24
- **Failure Types**:
  - Query parsing errors: 1
  - Data retrieval timeout: 1

### Tough Query Failures
- **Failed Queries**: 3/20
- **Failure Types**:
  - No parallel entities found: 3
  - Affected queries:
    1. "Which driver performs best in the rain?"
    2. "What team has improved the most over the last 5 seasons?"
    3. "How does Ferrari perform compared to Red Bull in wet conditions?"

## Performance Bottlenecks
1. **Entity Detection**:
   - Struggles with implicit multi-entity queries
   - Cannot handle comparative terms effectively

2. **Query Processing**:
   - Higher latency for historical queries (avg +0.14s)
   - Parallel fetch overhead for multi-entity queries

3. **Caching**:
   - No cache utilization in first runs
   - Cache key generation overhead (~0.02s per query)

## Recommendations
1. **Short-term Improvements**:
   - Implement semantic entity detection
   - Add retry logic for failed API fetches
   - Optimize cache key generation

2. **Long-term Optimizations**:
   - Add predictive caching for common query patterns
   - Implement query result aggregation
   - Enhance parallel processing for multi-entity queries 