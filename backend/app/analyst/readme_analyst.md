# F1 Data Analyst Module

## Overview
The analyst module integrates three key components of the F1 data analysis pipeline:
1. Query Processing
2. Data Pipeline
3. Analysis & Visualization

## Implementation Details

### Query Processing
- Uses `QueryProcessor` to convert natural language queries into structured API requirements
- Handles different query categories:
  - Basic Statistics
  - Driver Comparisons
  - Historical Trends

### Data Pipeline
- Makes HTTP requests to the F1 API (api.jolpi.ca/ergast)
- Handles different endpoint types:
  - Race results
  - Driver information
  - Constructor data
- Features:
  - Rate limiting (1-second delay between requests)
  - Automatic retries for failed requests
  - Error handling and logging

### Analysis & Visualization
- Converts API JSON responses to pandas DataFrames
- Generates Python code for data analysis
- Creates visualizations using matplotlib/seaborn
- Handles different data structures:
  - Single season data
  - Multi-season historical data
  - Race results and statistics

## Testing

### Integration Tests (`test_analyst.py`)
- Tests full pipeline integration
- Metrics tracked:
  - Code generation success/failure
  - Code execution success/failure
  - Visualization generation success/failure
  - Processing time per query

### Test Categories
1. Basic Stats Queries
   - Example: "Who won the most races in 2023?"
2. Driver Comparison Queries
   - Example: "Compare Verstappen and Hamilton's wins in 2023"
3. Historical Trend Queries
   - Example: "How has Ferrari's win rate changed since 2015?"

## Recent Changes

### API Integration
- Updated to use alternative F1 API endpoint (api.jolpi.ca/ergast)
- Added trailing slash handling for endpoints
- Improved error handling for API responses

### Data Processing
- Implemented JSON to DataFrame conversion for different response types
- Added season information to DataFrame when missing
- Fixed issues with data type conversion (season, round numbers)

### Code Generation
- Updated code generation to handle raw JSON and DataFrame inputs
- Improved error handling in generated code
- Added data validation before code execution

### Performance Improvements
- Added rate limiting to prevent API throttling
- Implemented batched processing for historical queries
- Added retries for failed API requests

## Usage

### Environment Setup
Required environment variables:
- `OPENAI_API_KEY`: For code generation
- `ANTHROPIC_API_KEY`: For query processing

### Running Tests
```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install httpx python-dotenv pandas

# Run tests
PYTHONPATH=backend python backend/app/analyst/test_analyst.py
```

## Success Metrics
Current performance metrics:
- Code Generation: 100% success rate
- Code Execution: 100% success rate
- Visualization Generation: 100% success rate
- Average Processing Time: ~17.5 seconds per query 