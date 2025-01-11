# Query Processing Test Cases

This document lists all test queries from `test_runner.py` and their expected `DataRequirements` mappings, along with their HTTP API request handling.

## Natural Language to Stats Queries

1. "Who won the most races in 2023?"
```python
DataRequirements(
    endpoint="/api/f1/races",
    params={
        "season": "2023",
        "limit": "all"
    }
)

# HTTP API Request
GET http://ergast.com/api/f1/2023/results.json?limit=1000
Response: List of race winners for 2023 season
```

2. "What is the fastest lap time recorded in 2023?"
```python
DataRequirements(
    endpoint="/api/f1/laps",
    params={
        "season": "2023",
        "fastest": "1"
    }
)

# HTTP API Request
GET http://ergast.com/api/f1/2023/fastest/1/laps.json
Response: Fastest lap times for each race in 2023
```

3. "Which team has the most podium finishes this season?"
```python
DataRequirements(
    endpoint="/api/f1/standings/constructors",
    params={
        "season": "2023"
    }
)

# HTTP API Request
GET http://ergast.com/api/f1/2023/constructorStandings.json
Response: Constructor standings with podium statistics
```

4. "How many races has Verstappen won in 2023?"
```python
DataRequirements(
    endpoint="/api/f1/drivers",
    params={
        "driver": "max_verstappen",
        "season": "2023",
        "position": "1"
    }
)

# HTTP API Request
GET http://ergast.com/api/f1/2023/drivers/max_verstappen/results/1.json
Response: Race wins for Verstappen in 2023
```

5. "What is the average lap time for Hamilton in 2023?"
```python
DataRequirements(
    endpoint="/api/f1/laps",
    params={
        "driver": "lewis_hamilton",
        "season": "2023"
    }
)

# HTTP API Request
GET http://ergast.com/api/f1/2023/drivers/lewis_hamilton/laps.json
Response: All lap times for Hamilton in 2023
```

## Driver Comparisons

6. "Compare Verstappen and Hamilton's wins in 2023"
```python
DataRequirements(
    endpoint="/api/f1/drivers",
    params={
        "driver": ["max_verstappen", "lewis_hamilton"],
        "season": "2023",
        "position": "1"
    }
)

# HTTP API Requests (Multiple)
GET http://ergast.com/api/f1/2023/drivers/max_verstappen/results/1.json
GET http://ergast.com/api/f1/2023/drivers/lewis_hamilton/results/1.json
Response: Race wins for both drivers in 2023
```

7. "Who has more podium finishes: Leclerc or Norris in 2023?"
```python
DataRequirements(
    endpoint="/api/f1/drivers",
    params={
        "driver": ["charles_leclerc", "lando_norris"],
        "season": "2023",
        "position": ["1", "2", "3"]
    }
)

# HTTP API Requests (Multiple)
GET http://ergast.com/api/f1/2023/drivers/charles_leclerc/results.json?position=1,2,3
GET http://ergast.com/api/f1/2023/drivers/lando_norris/results.json?position=1,2,3
Response: Podium finishes for both drivers
```

8. "Compare lap times between Verstappen and Alonso in Monaco 2023"
```python
DataRequirements(
    endpoint="/api/f1/laps",
    params={
        "driver": ["max_verstappen", "fernando_alonso"],
        "season": "2023",
        "circuit": "monaco"
    }
)

# HTTP API Requests (Multiple)
GET http://ergast.com/api/f1/2023/circuits/monaco/drivers/max_verstappen/laps.json
GET http://ergast.com/api/f1/2023/circuits/monaco/drivers/fernando_alonso/laps.json
Response: Lap times for both drivers at Monaco
```

## Historical Trends

9. "How has Ferrari's win rate changed since 2015?"
```python
DataRequirements(
    endpoint="/api/f1/constructors",
    params={
        "constructor": "ferrari",
        "season": list(map(str, range(2015, 2024))),
        "position": "1"
    }
)

# HTTP API Request (Multiple seasons)
GET http://ergast.com/api/f1/{season}/constructors/ferrari/results/1.json
# Repeated for each season from 2015 to 2023
Response: Ferrari's wins for each season
```

10. "What are Red Bull's podium finishes from 2010 to 2023?"
```python
DataRequirements(
    endpoint="/api/f1/constructors",
    params={
        "constructor": "red_bull",
        "season": list(map(str, range(2010, 2024))),
        "position": ["1", "2", "3"]
    }
)

# HTTP API Request (Multiple seasons)
GET http://ergast.com/api/f1/{season}/constructors/red_bull/results.json?position=1,2,3
# Repeated for each season from 2010 to 2023
Response: Red Bull's podium finishes per season
```

## Complex Queries

11. "Compare Verstappen's performance in rainy races vs dry races in the last 5 seasons"
```python
DataRequirements(
    endpoint="/api/f1/drivers",
    params={
        "driver": "max_verstappen",
        "season": list(map(str, range(2019, 2024))),
        "weather": ["wet", "dry"]
    }
)

# HTTP API Requests (Multiple with external weather data)
GET http://ergast.com/api/f1/{season}/drivers/max_verstappen/results.json
# Repeated for each season from 2019 to 2023
# Note: Weather data requires additional external API integration
Response: Race results combined with weather data
```

12. "Show me races where Ferrari outperformed Red Bull in qualifying but lost the race in 2023"
```python
DataRequirements(
    endpoint="/api/f1/qualifying",
    params={
        "constructor": ["ferrari", "red_bull"],
        "season": "2023"
    }
)

# HTTP API Requests (Multiple endpoints)
GET http://ergast.com/api/f1/2023/constructors/ferrari/qualifying.json
GET http://ergast.com/api/f1/2023/constructors/red_bull/qualifying.json
GET http://ergast.com/api/f1/2023/constructors/ferrari/results.json
GET http://ergast.com/api/f1/2023/constructors/red_bull/results.json
Response: Qualifying and race results for comparison
```

## Notes on API Handling

1. **Rate Limiting**: The Ergast API has a rate limit of 4 requests per second for the free tier.
2. **Pagination**: Use `limit` and `offset` parameters for large result sets (default limit is 30).
3. **Caching**: Implement caching for frequently accessed historical data.
4. **Error Handling**:
   - Handle 404 errors for invalid driver/constructor names
   - Handle rate limit responses (429)
   - Implement retry logic for failed requests
5. **Data Processing**:
   - Parse JSON responses into DataFrame format
   - Join multiple API responses for complex queries
   - Handle missing or null values in responses
6. **Performance Optimization**:
   - Use parallel requests where possible
   - Batch historical queries
   - Cache common lookup values (driver IDs, constructor IDs)