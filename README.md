## Peel

## Status of API Endpoints

### Working Endpoints ✅

1. **/connect_user** - WORKS
```python
import testing_api
tester = testing_api.TypeRacerAPITester('http://localhost:8000/api/v1', 'barat_paim')
tester.test_connect_user()
```

2. **/fetch_data** - WORKS
```python
tester.test_fetch_data()
```

3. **/load_data** - WORKS
```python
tester.test_load_data()
```

4. **/generate_code** - WORKS
```python
tester.test_generate_code()
```
Example output:
```json
{
  "status": "success",
  "code": "import pandas as pd\nimport seaborn as sns\n\n# Calculate average speed\nresult = df['speed'].mean()\n"
}
```

5. **/execute_code** - WORKS
```python
tester.test_execute_code()
```
Example output:
```json
{
  "status": "success",
  "result": "84.281",
  "modified_code": "import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\n\n# Calculate average speed\nresult = df['speed'].mean()\n"
}
```

6. **/query_guidance** - WORKS
```python
tester.test_query_guidance()
```
Example output:
```json
{
  "status": "success",
  "metadata": {
    "available_levels": ["Basic", "Intermediate", "Advanced", "Expert", "Users"],
    "available_categories": ["Dataset Understanding", "Summary Statistics", "Performance Trends", "Segment Analysis", "..."],
    "filters_applied": {
      "level": null,
      "category": null
    }
  },
  "questions": [
    {
      "id": 1,
      "question": "What are the key columns in this dataset, and what does each column represent?"
    },
    ...
  ]
}
```

### Next Steps 🚧

7. **/player_dashboard** - Next to implement

## API Endpoints Reference

| **Endpoint**        | **Method** | **Description**                                   | **Status**    |
|---------------------|------------|--------------------------------------------------|---------------|
| `/connect_user`     | POST       | Connects a user and fetches TypeRacer data       | ✅ Working    |
| `/fetch_data`       | POST       | Fetch race data for a user                       | ✅ Working    |
| `/load_data`        | GET        | Load data from PostgreSQL database               | ✅ Working    |
| `/generate_code`    | POST       | Generate Python code for queries                 | ✅ Working    |
| `/execute_code`     | POST       | Execute the generated code securely              | ✅ Working    |
| `/query_guidance`   | GET        | Return suggested analysis questions              | ✅ Working    |
| `/player_dashboard` | GET        | Retrieve player statistics and dashboard         | 🚧 To Do      |

## Environment Setup

1. Database Setup (Required):
```bash
# Create database and user
createdb typeracer_db
createuser -s postgres
psql postgres -c "ALTER USER postgres WITH PASSWORD 'your_password';"

# Add to .env file
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/typeracer_db
ANTHROPIC_API_KEY=your_anthropic_api_key

# Verify database connection
python app/utils/check_database.py
```

2. Run the server:
```bash
uvicorn app.main:app --reload
```

3. Run tests:
```python
import testing_api
tester = testing_api.TypeRacerAPITester('http://localhost:8000/api/v1', 'barat_paim')

# Test all working endpoints
tester.test_connect_user()
tester.test_fetch_data()
tester.test_load_data()
tester.test_generate_code()
tester.test_execute_code()
tester.test_query_guidance()
```

## Example Queries

The `/generate_code` endpoint supports various analysis questions, such as:
- "What is my average typing speed?"
- "Show my speed trend over time"
- "What is my fastest race?"

The generated code can then be executed using the `/execute_code` endpoint to get results and visualizations.

## Query Guidance

The `/query_guidance` endpoint helps users discover analysis questions. Features include:

1. **Filtering Options**:
   - `level`: Filter by difficulty (Basic, Intermediate, Advanced, Expert, Users)
   - `category`: Filter by category (Dataset Understanding, Performance Trends, etc.)
   - `query`: Search for questions using natural language
   - `max_suggestions`: Control the number of suggestions returned (default: 5)

2. **Example Usage**:
```bash
# Get all questions
curl http://localhost:8000/api/v1/query_guidance

# Filter by level
curl http://localhost:8000/api/v1/query_guidance?level=Basic

# Filter by category
curl http://localhost:8000/api/v1/query_guidance?category=Performance%20Trends

# Search for specific questions
curl http://localhost:8000/api/v1/query_guidance?query=typing%20speed

# Combine filters with search
curl http://localhost:8000/api/v1/query_guidance?level=Basic&category=Summary%20Statistics&query=average

# Control number of suggestions
curl http://localhost:8000/api/v1/query_guidance?max_suggestions=3
```

3. **Question Categories**:
   - Dataset Understanding: Basic questions about data structure and content
   - Summary Statistics: Statistical analysis of typing performance
   - Performance Trends: Analysis of performance changes over time
   - Segment Analysis: Analysis of performance in different contexts
   - Outlier Detection: Identification of unusual typing sessions
   - Fatigue Analysis: Analysis of performance degradation
   - Comparative Analysis: Comparison of performance across different conditions
   - Personal Performance Analysis: Individual user-focused analysis
   - Skill Classification: Assessment of typing skill level
   - And more...

4. **Search Features**:
   - Exact match: Returns questions that exactly match the search query
   - Substring match: Returns questions containing the search terms
   - Word match: Returns questions with matching keywords
   - Relevance scoring: Results are sorted by relevance to the query

5. **Response Format**:
```json
{
  "status": "success",
  "metadata": {
    "available_levels": ["Basic", "Intermediate", "Advanced", "Expert", "Users"],
    "available_categories": ["Dataset Understanding", "Performance Trends", ...],
    "filters_applied": {
      "level": "Basic",
      "category": "Summary Statistics",
      "query": "average speed",
      "max_suggestions": 5
    }
  },
  "questions": [
    {
      "id": 5,
      "question": "What is the average, minimum, and maximum typing speed (WPM) in this dataset?",
      "level": "Basic",
      "category": "Summary Statistics"
    },
    ...
  ]
}
```

## Data Pipeline

### Pipeline Components

1. **Data Ingestion**
   - F1 API data fetching
   - TypeRacer data fetching
   - Performance monitoring

2. **Data Normalization**
   - F1 race data normalization
   - F1 standings data normalization
   - TypeRacer data normalization
   - Schema validation

3. **Data Validation**
   - Input validation
   - Schema validation
   - Data type checking
   - Performance metrics validation

### Usage Examples

1. **F1 Driver Standings**
```python
from app.utils.platform_fetcher import fetch_platform_data
from app.utils.normalizer import DataNormalizer

# Fetch driver standings
raw_data = await fetch_platform_data("f1", "max_verstappen", "driver_standings")

# Normalize data
normalizer = DataNormalizer()
normalized_data = normalizer.normalize_f1_standings_data(raw_data)

# Access driver data
driver_standings = normalized_data["driver_standings"]
drivers = normalized_data["drivers"]
constructors = normalized_data["constructors"]
```

2. **TypeRacer Data**
```python
# Fetch TypeRacer data
raw_data = await fetch_platform_data("typeracer", "username", "user_stats")

# Normalize data
normalizer = DataNormalizer()
normalized_data = normalizer.normalize_typeracer_data(raw_data)

# Access normalized data
wpm = normalized_data["wpm"]
accuracy = normalized_data["accuracy"]
session_id = normalized_data["session_id"]
```

### Running Tests

1. **Integration Tests**
```bash
# Run all integration tests
pytest tests/test_pipeline_integration.py -v

# Run specific test categories
pytest tests/test_pipeline_integration.py -v -m "real_api"  # Real API tests
pytest tests/test_pipeline_integration.py -v -m "performance"  # Performance tests
```

2. **Test Categories**
   - Pipeline Flow Tests: Verify complete data pipeline
   - Cross-Platform Tests: Verify data consistency
   - Error Handling Tests: Verify error cases
   - Performance Tests: Verify timing thresholds
   - Real API Tests: Test with actual API data

3. **Performance Thresholds**
```python
PERFORMANCE_THRESHOLDS = {
    "ingestion_time": 2.0,  # seconds
    "normalization_time": 1.0,
    "query_processing_time": 3.0,
    "total_pipeline_time": 7.0
}
```
