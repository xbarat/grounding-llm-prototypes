## Peel

## Updates

**/connect_user** - WORKS
```python -c "
import testing_api
tester = testing_api.TypeRacerAPITester('http://localhost:8000/api/v1', 'barat_paim')
tester.test_connect_user()
"
```

**/fetch_data** - WORKS
```python -c "
import testing_api
tester = testing_api.TypeRacerAPITester('http://localhost:8000/api/v1', 'barat_paim')
tester.test_fetch_data()
"
```


---

## API Endpoints

| **Endpoint**        | **Method** | **Description**                                   | **Python Function**                     |
|---------------------|------------|---------------------------------------------------|-----------------------------------------|
| `/connect_user`     | POST       | Connects a user and fetches TypeRacer data.      | `fetch_user_stats()`                   |
| `/fetch_data`       | POST       | Fetch race data for a user.                       | `fetch_data()`                         |
| `/load_data`        | GET        | Load data from the SQLite database.               | `load_data_from_db()`                  |
| `/generate_code`    | POST       | Generate Python code for queries.                 | `generate_code()`                      |
| `/execute_code`     | POST       | Execute the generated code securely.              | `execute_code_safely()`                |
| `/player_dashboard`  | GET        | Retrieve player statistics and dashboard.         | `get_player_stats()`                   |
| `/query_guidance`   | GET        | Return suggestions for user queries.              | `QueryGuidance().filter_questions()`   |

---
