# GIRAFFE Backend Architecture Explainer

This document explains the structure and components of the GIRAFFE backend application.

## Directory Structure

```
backend/app/
├── database/         # Database configuration and operations
├── models/          # Data models and schemas
├── routes/          # API endpoints and route handlers
├── utils/           # Utility functions and helpers
├── main.py         # Application entry point
└── __init__.py     # Package initialization
```

## Core Components

### 1. Main Application (`main.py`)
- Entry point for the FastAPI application
- Configures middleware, routes, and database connections
- Sets up CORS and authentication
- Initializes the application state and dependencies

### 2. Database Layer (`database/`)
- `config.py`: Database connection configuration and settings
- `operations.py`: Database CRUD operations and query functions
- Handles PostgreSQL connection pooling and session management

### 3. Data Models (`models/`)
- `f1_models.py`: Formula 1 data models and schemas
  - Driver standings
  - Race results
  - Qualifying data
  - Circuit information
- `typing_stats.py`: TypeRacer statistics models
  - Race history
  - User performance metrics
  - Typing accuracy data

### 4. API Routes (`routes/`)
- `platforms.py`: Platform-specific endpoints
  - Platform connection and verification
  - Data fetching endpoints
  - Platform configuration
- `analysis.py`: Data analysis endpoints
  - Query processing
  - Data visualization
  - Analysis results
- `data.py`: Data management endpoints
  - Raw data access
  - Cache management
- `user.py`: User management endpoints
  - Authentication
  - User preferences
  - Session management

### 5. Utility Modules (`utils/`)

#### Data Processing
- `normalizer.py`: Data normalization pipeline
  - Platform-specific data normalization
  - Schema validation
  - Data cleaning and formatting

- `pipeline_validator.py`: Data pipeline validation
  - Input validation
  - Schema verification
  - Data quality checks
  - Performance monitoring

- `platform_fetcher.py`: External API integration
  - API request handling
  - Rate limiting
  - Error handling
  - Response caching

#### Query Processing
- `query_processor.py`: Natural language query processing
  - Query parsing and validation
  - API endpoint mapping
  - Analysis requirements extraction
  - Claude integration for query understanding

- `code_utils.py`: Code generation utilities
  - Analysis code generation
  - Code validation
  - Error handling
  - Performance optimization

#### Platform Integration
- `f1_api.py`: Formula 1 API client
  - Ergast API integration
  - Data fetching
  - Response parsing
  - Cache management

- `platform_config.py`: Platform configuration
  - API endpoints
  - Authentication settings
  - Rate limits
  - Cache durations

#### Monitoring and Performance
- `pipeline_monitor.py`: Pipeline monitoring
  - Performance metrics
  - Error tracking
  - Resource usage
  - Bottleneck detection

#### Helper Utilities
- `prompts.py`: Claude prompt templates
  - Query processing prompts
  - Code generation prompts
  - Error handling prompts

- `variable_mapper.py`: Variable mapping
  - Data field mapping
  - Type conversion
  - Schema alignment

- `plotting.py`: Visualization utilities
  - Chart generation
  - Plot formatting
  - Data visualization helpers

## Data Flow

1. **Query Processing Flow**
   ```
   User Query → Query Processor → API Endpoint Selection → Data Fetching →
   Data Normalization → Analysis → Visualization
   ```

2. **Data Pipeline Flow**
   ```
   Platform API → Data Fetcher → Normalizer → Validator → Database →
   Cache → API Response
   ```

3. **Analysis Flow**
   ```
   Query → Claude Processing → Code Generation → Data Transformation →
   Analysis Execution → Results Formatting → Visualization
   ```

## Integration Points

### 1. External APIs
- Formula 1 (Ergast API)
  - Driver standings
  - Race results
  - Qualifying data
- TypeRacer API
  - Race history
  - User statistics
  - Performance metrics

### 2. Database Integration
- PostgreSQL for persistent storage
- Connection pooling
- Query optimization
- Cache management

### 3. LLM Integration (Claude)
- Query processing
- Code generation
- Error handling
- Response formatting

## Performance Considerations

1. **Caching Strategy**
   - API response caching
   - Database query caching
   - Analysis results caching
   - Cache invalidation rules

2. **Performance Monitoring**
   - Query processing time
   - API response time
   - Analysis execution time
   - Resource utilization

3. **Error Handling**
   - API failures
   - Data validation errors
   - Processing errors
   - Resource constraints

## Security Measures

1. **API Security**
   - Rate limiting
   - Request validation
   - Authentication
   - CORS configuration

2. **Data Security**
   - Input sanitization
   - Output validation
   - Secure data storage
   - Access control

## Future Enhancements

1. **Planned Features**
   - Additional platform integrations
   - Enhanced visualization options
   - Advanced analytics capabilities
   - Real-time data processing

2. **Scalability**
   - Distributed processing
   - Load balancing
   - Database optimization
   - Cache distribution 