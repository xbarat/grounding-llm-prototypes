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

### Next Steps 🚧

6. **/player_dashboard** - Next to implement
7. **/query_guidance** - Next to implement

## API Endpoints Reference

| **Endpoint**        | **Method** | **Description**                                   | **Status**    |
|---------------------|------------|--------------------------------------------------|---------------|
| `/connect_user`     | POST       | Connects a user and fetches TypeRacer data       | ✅ Working    |
| `/fetch_data`       | POST       | Fetch race data for a user                       | ✅ Working    |
| `/load_data`        | GET        | Load data from PostgreSQL database               | ✅ Working    |
| `/generate_code`    | POST       | Generate Python code for queries                 | ✅ Working    |
| `/execute_code`     | POST       | Execute the generated code securely              | ✅ Working    |
| `/player_dashboard` | GET        | Retrieve player statistics and dashboard         | 🚧 To Do      |
| `/query_guidance`   | GET        | Return suggestions for user queries              | 🚧 To Do      |

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
```

## Example Queries

The `/generate_code` endpoint supports various analysis questions, such as:
- "What is my average typing speed?"
- "Show my speed trend over time"
- "What is my fastest race?"

The generated code can then be executed using the `/execute_code` endpoint to get results and visualizations.
