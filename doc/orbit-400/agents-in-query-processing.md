Here’s how you can craft two agents—one for query understanding and parameter recognition and one for endpoint mapping—to fully leverage the available API endpoints:

Agent 1: Query Understanding and Parameter Recognition

Responsibilities:
	1.	Parse the user query into structured parameters (action, entities, and optional filters).
	2.	Handle dynamic ranges (e.g., “last 5 seasons,” “Hamilton’s fastest laps”).
	3.	Output a JSON structure with actionable parameters.

Prompt Template:

```text
You are an expert query parser for F1 data. Your job is to extract the structured parameters from natural language queries. Provide the response in JSON format. Include:
1. `action`: The type of query (e.g., "rank", "compare", "fetch").
2. `entity`: The target (e.g., "driver", "constructor", "race").
3. `parameters`: Specific details extracted from the query (e.g., season, round, driver, constructor).

Available Parameters:
- `season`: Specific year (e.g., "2023") or range (e.g., "last 5 seasons").
- `round`: Race number in a season.
- `driver`: Driver name (e.g., "lewis_hamilton").
- `constructor`: Constructor name (e.g., "red_bull").

### Examples:
1. Query: "How many races has Lewis Hamilton won in 2023?"
   Output: {"action": "fetch", "entity": "results", "parameters": {"season": "2023", "driver": "lewis_hamilton"}}

2. Query: "Show the constructors' standings after the 5th race in 2022."
   Output: {"action": "fetch", "entity": "standings", "parameters": {"season": "2022", "round": 5, "constructor": true}}

3. Query: "Get Verstappen's rank changes over the last 5 seasons."
   Output: {"action": "rank", "entity": "drivers", "parameters": {"season_range": [2018, 2019, 2020, 2021, 2022], "driver": "max_verstappen"}}

Now parse the following query:
{insert user query here}
```

Output Example:

For the query:
“How has Max Verstappen’s rank changed across the last 10 seasons?”
The agent would produce:

{
  "action": "rank",
  "entity": "drivers",
  "parameters": {
    "season_range": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    "driver": "max_verstappen"
  }
}

Agent 2: Endpoint Mapping

Responsibilities:
	1.	Map the parsed query parameters to the correct API endpoint.
	2.	Handle parameter substitution dynamically (e.g., filling in driver or season).
	3.	Return a ready-to-use API call.

Prompt Template:

```text
You are an endpoint mapping assistant for an F1 data system. Your task is to match extracted parameters to the correct API endpoint and format the response as a ready-to-use API call. Use the following endpoint descriptions:

### Endpoints:
1. `/api/f1/races`: Gets race results for a season.
   - Parameters: `season`
2. `/api/f1/results`: Gets specific race results.
   - Parameters: `season`, `round`
3. `/api/f1/qualifying`: Gets qualifying results.
   - Parameters: `season`, optional `round`
4. `/api/f1/drivers`: Gets results for specific drivers.
   - Parameters: `season`, `driver`
5. `/api/f1/constructors`: Gets results for constructors.
   - Parameters: `season`, `constructor`
6. `/api/f1/standings/drivers`: Gets driver championship standings.
   - Parameters: `season`, `round`
7. `/api/f1/standings/constructors`: Gets constructor standings.
   - Parameters: `season`, `round`
8. `/api/f1/status`: Gets race status.
   - Parameters: `season`
9. `/api/f1/circuits`: Gets circuit info.
   - Parameters: `season`

### Examples:
1. Input: {"action": "fetch", "entity": "results", "parameters": {"season": "2023", "driver": "lewis_hamilton"}}
   Output: {"endpoint": "/api/f1/drivers", "params": {"season": "2023", "driver": "lewis_hamilton"}}

2. Input: {"action": "rank", "entity": "drivers", "parameters": {"season_range": [2018, 2019, 2020], "driver": "max_verstappen"}}
   Output: {"endpoint": "/api/f1/standings/drivers", "params": {"season_range": [2018, 2019, 2020], "driver": "max_verstappen"}}

Now map the following input to an API endpoint:
{insert structured parameters here}
```

Output Example:

For the parsed parameters:

```json
{
  "action": "rank",
  "entity": "drivers",
  "parameters": {
    "season_range": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    "driver": "max_verstappen"
  }
}
```

The agent would produce:

```json
{
  "endpoint": "/api/f1/standings/drivers",
  "params": {
    "season_range": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    "driver": "max_verstappen"
  }
}
```

How These Agents Work Together
	1.	Agent 1:
	•	Extracts intent and parameters (e.g., action, entity, season range, driver).
	•	Outputs a structured JSON object.
	2.	Agent 2:
	•	Maps the structured JSON object to the correct API endpoint and generates a ready-to-use API call.
	3.	Workflow:
	•	User Query → Agent 1 → Parsed Parameters → Agent 2 → API Call

Benefits of This Setup
	1.	Modularity:
	•	You can debug and optimize query parsing and endpoint mapping independently.
	2.	Scalability:
	•	Add new endpoints or entities easily without retraining the entire system.
	3.	Accuracy:
	•	Separating concerns ensures better accuracy for both understanding and mapping.

With these agents, your system will be able to expertly leverage the full powers of the database!