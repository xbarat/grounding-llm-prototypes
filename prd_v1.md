# GIRAFFE v0.9 Requirements Document

## 1. System Architecture

### 1.1 Backend (FastAPI)
- **Core Components**:
  - Platform Configuration Manager
  - Data Fetcher Service
  - Analysis Engine
  - Authentication System
  - Database Integration
  - Data Pipeline Service
    - Ingestion Layer
    - Normalization Layer
    - Validation Layer
    - Performance Monitoring

### 1.2 Frontend (Next.js)
- **Core Components**:
  - Platform Selection Interface
  - Connection Management
  - Query Interface
  - Visualization Display
  - User Dashboard

## 2. Platform Integration

### 2.1 TypeRacer Integration
- **Base URL**: `data.typeracer.com`
- **Endpoints**:
  - `/pit/race_history`: Get user's race history
    - Parameters: `n=100&username={username}`
    - Returns: Last 100 races with speed, accuracy, and rank
  - `/users`: Get user profile data
    - Parameters: `username={username}`
    - Returns: Overall stats, account info, achievements
  - `/text_stats`: Get typing statistics
    - Parameters: `username={username}`
    - Returns: Average speed, best speed, races completed
- **Authentication**: Username-based
- **Rate Limits**: Standard API limits
- **Data Format**: JSON

### 2.2 Formula 1 Integration
- **Base URL**: `http://ergast.com/api/f1`
- **Endpoints**:
  - `/current/driverStandings.json`: Get current driver standings
    - Returns: Points, position, wins per driver
    - Normalized Schema: 
      ```python
      {
          "drivers": List[Dict],  # Driver details
          "constructors": List[Dict],  # Constructor details
          "driver_standings": List[Dict]  # Current standings
      }
      ```
  - `/current.json`: Get current season information
  - `/current/constructorStandings.json`: Get constructor standings
  - `/current/last/results.json`: Get last race results
  - `/current/last/qualifying.json`: Get last qualifying results
  - `/drivers/{driverId}/results.json`: Get specific driver results
  - `/circuits/{circuitId}/results.json`: Get circuit-specific results
- **Rate Limits**: 4 requests/second
- **Data Format**: JSON
- **Authentication**: Not required
- **Cache Strategy**: Results cached for 1 hour

## 3. Database Requirements

### 3.1 PostgreSQL Configuration
- **Connection**: psycopg v3.2.3
- **Schema Requirements**:
  - User profiles
  - Platform-specific data
  - Analysis results cache
- **Environment Variables**:
  - DATABASE_URL
  - Connection pooling settings

### 3.2 Data Models
- **TypeRacer Stats**:
  - Speed metrics
  - Accuracy data
  - Game history
- **F1 Stats**:
  - Driver performance
  - Race results
  - Team statistics

## 4. API Structure

### 4.1 Core Endpoints
- `/api/v1/platforms`: List available platforms
- `/api/v1/platforms/{platform}/verify`: Verify user credentials
- `/api/v1/platforms/{platform}/connect`: Connect to platform
- `/api/v1/platforms/{platform}/queries`: Get platform-specific queries
- `/api/v1/platforms/analyze`: Perform data analysis

### 4.2 Authentication Flow
1. Platform selection
2. Identifier verification
3. Initial data fetch
4. Connection persistence

## 5. Frontend Requirements

### 5.1 UI Components
- **Required Components**:
  - ConnectForm
  - Sidebar
  - QueryResults
  - PlatformSelector
  - Visualizations

### 5.2 State Management
- **Auth State**:
  - User information
  - Platform connection
  - Session persistence
- **Query State**:
  - Current query
  - Results cache
  - Error handling

## 6. Analysis Engine

### 6.0 Query Processing Pipeline

#### Implementation Plan (Claude Integration)

1. **Query Processor Class Structure**:
```python
class QueryProcessor:
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.system_prompt = """
        You are a query processing expert that converts natural language queries 
        about F1 and TypeRacer data into structured API calls and analysis requirements.
        Available F1 endpoints:
        - /current/driverStandings.json
        - /drivers/{driverId}/results.json
        - /current/last/results.json
        Available TypeRacer endpoints:
        - /pit/race_history
        - /text_stats
        """

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query into API calls and analysis requirements."""
        prompt = self._build_prompt(query)
        response = await self.client.generate(prompt)
        return self._parse_response(response)

    def _build_prompt(self, query: str) -> str:
        return f"""
        Convert this query into API calls and analysis requirements:
        {query}

        Output must be valid JSON with this structure:
        {{
            "api_calls": [
                {{
                    "endpoint": str,
                    "parameters": dict,
                    "required_fields": list[str]
                }}
            ],
            "analysis_requirements": {{
                "metrics": list[str],
                "visualization": str,
                "additional_processing": dict
            }}
        }}
        """

2. **Query Categories and Templates**:
```python
QUERY_TEMPLATES = {
    "driver_performance": {
        "pattern": r"(.*performance.*|.*results.*|.*stats.*) (for|of) (?P<driver>.*)",
        "api_template": {
            "endpoint": "/drivers/{driver}/results.json",
            "required_fields": ["position", "points", "grid"]
        }
    },
    "race_comparison": {
        "pattern": r"compare (?P<driver1>.*) and (?P<driver2>.*)",
        "api_template": {
            "endpoint": [
                "/drivers/{driver1}/results.json",
                "/drivers/{driver2}/results.json"
            ]
        }
    },
    "typeracer_trend": {
        "pattern": r"(typing|speed|accuracy) (trend|history|progress)",
        "api_template": {
            "endpoint": "/pit/race_history",
            "parameters": {"n": 100}
        }
    }
}
```

3. **Response Processing**:
```python
class QueryResponse:
    def __init__(self, api_calls: List[Dict], analysis_reqs: Dict):
        self.api_calls = api_calls
        self.analysis_requirements = analysis_reqs

    async def execute(self) -> DataFrame:
        """Execute API calls and create DataFrame."""
        data = []
        for call in self.api_calls:
            response = await fetch_platform_data(
                endpoint=call["endpoint"],
                params=call["parameters"]
            )
            data.append(response)
        return self._create_dataframe(data)

    def _create_dataframe(self, data: List[Dict]) -> DataFrame:
        """Convert API responses to analysis-ready DataFrame."""
        # DataFrame creation logic
        pass
```

4. **Integration with Analysis Engine**:
```python
class AnalysisEngine:
    def __init__(self):
        self.query_processor = QueryProcessor(anthropic_client)
        
    async def process_analysis_request(self, query: str):
        # 1. Process query
        query_response = await self.query_processor.process_query(query)
        
        # 2. Execute API calls and create DataFrame
        df = await query_response.execute()
        
        # 3. Generate analysis code
        code = self.generate_analysis_code(
            df, 
            query_response.analysis_requirements
        )
        
        # 4. Execute analysis
        result = self.execute_analysis(code, df)
        
        return result
```

5. **Example Prompts and Responses**:
```python
# Example 1: Driver Performance
Input: "Show me Max Verstappen's performance trend in the last 5 races"
Output: {
    "api_calls": [
        {
            "endpoint": "/drivers/max_verstappen/results.json",
            "parameters": {"limit": 5},
            "required_fields": ["position", "points", "grid"]
        }
    ],
    "analysis_requirements": {
        "metrics": ["position", "points"],
        "visualization": "line_chart",
        "additional_processing": {
            "trend_analysis": True,
            "moving_average": 3
        }
    }
}

# Example 2: Multi-Driver Comparison
Input: "Compare Hamilton and Verstappen's qualifying performances"
Output: {
    "api_calls": [
        {
            "endpoint": "/drivers/hamilton/qualifying.json",
            "parameters": {"season": "current"},
            "required_fields": ["Q1", "Q2", "Q3", "position"]
        },
        {
            "endpoint": "/drivers/max_verstappen/qualifying.json",
            "parameters": {"season": "current"},
            "required_fields": ["Q1", "Q2", "Q3", "position"]
        }
    ],
    "analysis_requirements": {
        "metrics": ["Q3_time", "position"],
        "visualization": "dual_line_chart",
        "additional_processing": {
            "time_conversion": True,
            "head_to_head": True
        }
    }
}
```

6. **Error Handling and Validation**:
```python
class QueryValidationError(Exception):
    pass

class QueryValidator:
    def validate_query_response(self, response: Dict) -> bool:
        required_fields = ["api_calls", "analysis_requirements"]
        if not all(field in response for field in required_fields):
            raise QueryValidationError("Missing required fields")
        
        for call in response["api_calls"]:
            if not self._validate_api_call(call):
                raise QueryValidationError(f"Invalid API call: {call}")
        
        return True

    def _validate_api_call(self, call: Dict) -> bool:
        required_fields = ["endpoint", "parameters", "required_fields"]
        return all(field in call for field in required_fields)
```

7. **Performance Monitoring**:
```python
class QueryMetrics:
    def __init__(self):
        self.metrics = {
            "query_processing_time": [],
            "api_call_time": [],
            "analysis_time": []
        }

    def record_metric(self, metric_name: str, value: float):
        self.metrics[metric_name].append(value)

    def get_average(self, metric_name: str) -> float:
        values = self.metrics[metric_name]
        return sum(values) / len(values) if values else 0.0
```

### 6.1 Query Processing
- Natural language processing
- Query categorization
- Code generation
- Result formatting

### 6.2 Visualization Types
- Line charts
- Bar charts
- Scatter plots
- Heat maps
- Custom visualizations per platform

## 7. Testing Requirements

### 7.1 Backend Tests
- **Integration Tests**:
  - Platform API connectivity
    - Real API testing with F1 endpoints
    - Mock API testing for development
  - Data Pipeline Testing
    - Ingestion validation
    - Normalization verification
    - Cross-platform consistency
  - Performance Monitoring
    - Ingestion timing (< 2.0s)
    - Normalization timing (< 1.0s)
    - Total pipeline timing (< 7.0s)
  
  - Analysis accuracy
  - Cache validation
  - Error recovery

- **Unit Tests**:
  - Data normalization
  - Schema validation
  - Error handling
  - Performance metrics
  
  - Code generation
  - Query processing
  - Cache management

### 7.2 Frontend Tests
- Component rendering
- User interactions
- State management
- API integration

## 8. Development Environment

### 8.1 Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# [NEW] Run pipeline tests
pytest tests/test_pipeline_integration.py -v  # All pipeline tests
pytest tests/test_pipeline_integration.py -v -m "real_api"  # Real API tests
pytest tests/test_pipeline_integration.py -v -m "performance"  # Performance tests

uvicorn app.main:app --reload
```

### 8.2 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 8.3 Required Environment Variables
```env
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ANTHROPIC_API_KEY=your_key_here
# [NEW] Pipeline Configuration
PIPELINE_CACHE_DURATION=3600  # Cache duration in seconds
PIPELINE_MAX_RETRIES=3       # Maximum retries for failed requests
PIPELINE_TIMEOUT=30          # Request timeout in seconds

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 9. Deployment Considerations

### 9.1 Infrastructure
- PostgreSQL database
- API server
- Frontend hosting
- Cache system

### 9.2 Security
- API rate limiting
- CORS configuration
- Environment variable management
- Error logging
- Pipeline Security:
  - Request validation
  - Data sanitization
  - Performance monitoring
  - Error tracking

## 10. Future Enhancements

### 10.1 Planned Features
- Cricket data integration
- Enhanced visualization options
- User preferences storage
- Advanced analytics features

### 10.2 Scalability
- Caching strategy
- Database optimization
- API performance monitoring
- Load balancing considerations
- Pipeline Scalability:
  - Parallel processing
  - Batch normalization
  - Distributed validation
  - Performance optimization