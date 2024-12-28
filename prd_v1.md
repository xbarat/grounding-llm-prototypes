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
# [NEW DECISION REQUIRED] Query to API Translation Layer

#### Current Flow:
```
User Query (text) -> Code Generation -> DataFrame Analysis -> Visualization
```

#### Proposed Enhanced Flow:
```
User Query (text) -> Query Processing LLM -> API Endpoint Selection -> Data Fetching -> 
DataFrame Creation -> Code Generation -> Analysis -> Visualization
```

#### LLM Options Analysis:

1. **GPT-4**
   - Pros:
     - Excellent natural language understanding
     - Strong context handling for complex queries
     - Reliable API endpoint mapping
     - Can handle ambiguous queries well
   - Cons:
     - Higher cost per query
     - API rate limits
     - Closed source
     - Latency considerations

2. **Claude (Anthropic)**
   - Pros:
     - Strong reasoning capabilities
     - Good at structured output
     - Competitive pricing
     - Already integrated in our system
   - Cons:
     - Similar limitations as GPT-4
     - Less community resources
     - Potential vendor lock-in

3. **Open Source LLMs (Llama, etc.)**
   - Pros:
     - Self-hosted solution
     - No per-query costs
     - Customizable for our use case
     - No rate limits
   - Cons:
     - Infrastructure overhead
     - Lower performance than GPT-4/Claude
     - Requires fine-tuning
     - Higher maintenance effort

#### Example Query Processing:
```python
# Input Query
"Show me Max Verstappen's performance trend in the last 5 races"

# LLM Processing Required:
1. Identify entity (driver="max_verstappen")
2. Identify time range (last_n_races=5)
3. Identify metric (performance_trend=True)
4. Map to API endpoints:
   - /drivers/max_verstappen/results.json?limit=5
   - /current/driverStandings.json

# Output Structure:
{
    "api_calls": [
        {
            "endpoint": "/drivers/max_verstappen/results.json",
            "parameters": {"limit": 5},
            "required_fields": ["position", "points", "grid"]
        },
        {
            "endpoint": "/current/driverStandings.json",
            "parameters": {},
            "required_fields": ["points", "position", "wins"]
        }
    ],
    "analysis_requirements": {
        "trend_analysis": True,
        "metrics": ["position", "points"],
        "visualization": "line_chart"
    }
}
```

#### Decision Factors:
1. **Performance Requirements**:
   - Query processing time < 1s
   - Accuracy in endpoint mapping > 95%
   - Handle complex multi-endpoint queries

2. **Cost Considerations**:
   - Per-query cost vs. infrastructure cost
   - Development and maintenance effort
   - Training/fine-tuning costs

3. **Scalability**:
   - Query volume expectations
   - Infrastructure requirements
   - Maintenance overhead

4. **Development Timeline**:
   - GPT-4/Claude: 1-2 weeks
   - Open Source LLM: 3-4 weeks + training time

#### Recommendation:
Initial implementation using Claude (already integrated) with future migration path to self-hosted solution:

1. **Phase 1** (Current - 2 weeks):
   - Implement with Claude
   - Build query processing pipeline
   - Gather query patterns and training data

2. **Phase 2** (Future - 1 month):
   - Evaluate self-hosted LLM performance
   - Fine-tune on collected data
   - Implement hybrid approach if needed

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