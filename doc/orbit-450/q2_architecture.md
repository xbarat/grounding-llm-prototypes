# Q2 Architecture: Multi-Agent Query Processing System

## Overview
The Q2 (Query Quality) system is a multi-agent (currently 2 agents) architecture designed to improve query processing accuracy and reliability in the F1 data analysis platform. It employs a coordinated system of specialized agents to understand, process, and map natural language queries to appropriate API endpoints.

## System Components

### 1. Q2Processor
The main coordinator that manages the multi-agent workflow and ensures seamless integration with the existing system.
- Coordinates between Understanding and Mapping agents
- Handles error recovery and fallback mechanisms
- Maintains processing metrics and confidence scoring

### 2. UnderstandingAgent
Specializes in natural language understanding and parameter extraction.
- Uses enhanced GPT-4O Mini model for query interpretation
- Implements pattern matching for common query types
- Extracts structured parameters from natural language
- Maintains a cache of common patterns for quick matching

### 3. EndpointMappingAgent
Focuses on mapping structured parameters to specific API endpoints.
- Maps parsed parameters to appropriate F1 data endpoints
- Handles parameter transformation and validation
- Implements cached endpoint patterns for frequent queries
- Provides fallback to AI mapping for complex cases

## Data Structures

### Q2Parameters
Enhanced parameter structure for improved query understanding:
```python
{
    "action": str,      # rank, compare, fetch, analyze
    "entity": str,      # driver, constructor, race, qualifying
    "parameters": dict, # Extracted parameters
    "confidence": float # Confidence score
}
```

### Q2Result
Result structure with metadata for analysis:
```python
{
    "requirements": DataRequirements,
    "confidence": float,
    "processing_time": float,
    "agent_trace": List[str]
}
```

## Query Processing Flow

1. **Initial Processing**
   - Query received by Q2Processor
   - Pattern matching attempted for quick resolution
   - If no pattern match, proceed to detailed processing

2. **Understanding Phase**
   - Natural language query parsed by UnderstandingAgent
   - Parameters extracted and structured
   - Confidence score calculated

3. **Mapping Phase**
   - Structured parameters mapped to endpoints
   - Parameter transformation applied if needed
   - Endpoint requirements validated

4. **Result Generation**
   - Final requirements assembled
   - Metadata collected
   - Results returned with confidence score

## Caching System

The Q2 system implements two levels of caching:

1. **Pattern Cache**
   - Common query patterns cached
   - Regular expression based matching
   - High confidence direct matches

2. **Endpoint Cache**
   - Frequently used endpoint mappings
   - Parameter transformation templates
   - Quick lookup for common queries

## Error Handling

- Graceful degradation to simpler processing
- Detailed error tracking and logging
- Automatic retry with fallback options
- Error recovery strategies based on query type

## Performance Metrics

- Query processing time tracking
- Confidence score calculation
- Pattern match success rate
- Cache hit ratio monitoring
- Error rate tracking by query type

## Integration Points

1. **API Integration**
   - FastAPI endpoints
   - Authentication system
   - Data retrieval services

2. **Model Integration**
   - GPT-4O Mini interface
   - Model response parsing
   - Error handling

3. **Monitoring Integration**
   - Logging system
   - Performance metrics
   - Error tracking

## Security Considerations

- Authentication token validation
- Rate limiting implementation
- Input validation and sanitization
- Secure parameter handling
- Error message sanitization 