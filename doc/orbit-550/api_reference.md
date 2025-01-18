# API Reference Documentation

## Endpoints

### Query Processing
#### POST /api/v1/analyze
Process and analyze F1 data based on natural language queries.

**Request**
```json
{
  "query": "string"  // Natural language query about F1 data
}
```

**Response**
```json
{
  "success": boolean,
  "data": object,      // Analysis results
  "executed_code": string,  // Generated analysis code
  "query_trace": array,     // Query processing steps
  "processing_time": float, // Processing duration
  "metadata": object       // Additional processing info
}
```

**Error Response**
```json
{
  "success": false,
  "error": "Analysis failed",
  "details": string,
  "processing_time": float
}
```

### Data Structures

#### Constructor Data Format
```json
{
  "constructorId": "string",
  "url": "string",
  "name": "string",
  "nationality": "string",
  "performance": {
    "points": number,
    "position": number,
    "wins": number,
    "year": number
  }
}
```

#### DataFrame Structure
```python
# Standard DataFrame columns
required_columns = [
    'year',           # Season year
    'constructorId',  # Unique constructor identifier
    'points',         # Points scored
    'position',       # Championship position
    'wins',          # Race wins
    'nationality'     # Constructor nationality
]
```

### Error Codes
- `400`: Bad Request (Invalid query or data processing error)
- `404`: Not Found (No data available)
- `500`: Internal Server Error (Pipeline processing failure)

### Response Headers
```http
Content-Type: application/json
Access-Control-Allow-Origin: *
Cache-Control: public, max-age=300
```

## Internal Pipeline

### Data Flow
1. Query Processing → DataRequirements
2. Pipeline Processing → Raw Data
3. Data Validation → Clean Data
4. Data Normalization → Analysis Ready Data
5. Code Generation → Executable Analysis
6. Result Generation → API Response

### Data Validation Rules
1. Constructor data must be list or dict
2. Year values must be valid integers
3. Numeric fields must be numbers
4. Required fields must be present

### Performance Considerations
- Response time target: < 2 seconds
- Cache duration: 5 minutes
- Rate limiting: 100 requests/minute
- Maximum query length: 500 characters 