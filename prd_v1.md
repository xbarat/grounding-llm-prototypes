# GIRAFFE v0.9 Requirements Document

## 1. System Architecture

### 1.1 Backend (FastAPI)
- **Core Components**:
  - Platform Configuration Manager
  - Data Fetcher Service
  - Analysis Engine
  - Authentication System
  - Database Integration

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
  - `/current.json`: Get current season information
    - Returns: Race schedule, circuits, dates
  - `/current/driverStandings.json`: Get current driver standings
    - Returns: Points, position, wins per driver
  - `/current/constructorStandings.json`: Get constructor standings
    - Returns: Points, position, wins per team
  - `/current/last/results.json`: Get last race results
    - Returns: Final positions, times, points
  - `/current/last/qualifying.json`: Get last qualifying results
    - Returns: Q1/Q2/Q3 times, final grid positions
  - `/drivers/{driverId}/results.json`: Get specific driver results
    - Returns: All race results for specified driver
  - `/circuits/{circuitId}/results.json`: Get circuit-specific results
    - Returns: Historical race results for specified circuit
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
  - Data fetching reliability
  - Analysis accuracy
- **Unit Tests**:
  - Code generation
  - Data processing
  - Error handling

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