# Q2 System Setup Guide

## Directory Structure

```
backend/
├── app/
│   ├── query/                 # Q2 Query Processing System
│   │   ├── __init__.py
│   │   ├── processor.py      # Main Q2 processor implementation
│   │   ├── q2_assistants.py  # Q2 multi-agent system
│   │   ├── models.py         # Data models and structures
│   │   ├── test_runner.py    # Standard test suite
│   │   └── edge_test.py      # Edge case test suite
│   ├── pipeline/             # Data Processing Pipeline
│   │   ├── data2.py         # Enhanced data processing
│   │   ├── mappings.py      # Endpoint mappings
│   │   └── data_validator.py # Data validation
│   ├── auth/                 # Authentication
│   │   └── routes.py        # Auth endpoints
│   └── main.py              # FastAPI application
├── tests/                    # Test suites
└── requirements.txt          # Python dependencies
```

## Critical Files

### Core Implementation
- `q2_assistants.py`: Multi-agent system implementation
- `processor.py`: Main query processing logic
- `models.py`: Data structures and models

### Testing
- `test_runner.py`: Standard test suite
- `edge_test.py`: Edge case testing
- `query-test.txt`: Test queries collection

### Configuration
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (create from template)

## Setup Instructions

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate  # Unix/macOS
   # or
   .\venv\Scripts\activate   # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   ```bash
   # Create .env file
   cp .env.template .env
   
   # Required variables:
   OPENAI_API_KEY=your_api_key
   DATABASE_URL=your_db_url
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   python -m app.db_migrations
   
   # Initialize database
   python -m app.db_setup
   ```

## Testing Commands

### Standard Test Suite
```bash
# Run standard tests
python -m app.query.test_runner

# View results
cat query_test_results_*.json
```

### Edge Case Testing
```bash
# Run edge case tests
python -m app.query.edge_test

# View results
cat edge_test_results_*.json
```

### Performance Testing
```bash
# Run with timing
time python -m app.query.test_runner

# Run with profiling
python -m cProfile -o output.prof -m app.query.test_runner
```

## API Endpoints

### Core Endpoints
1. `/analyze` - Main query processing endpoint
   ```bash
   curl -X POST http://localhost:8000/analyze \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"query": "your query here"}'
   ```

2. `/health` - System health check
   ```bash
   curl http://localhost:8000/health
   ```

### Authentication
1. `/auth/login` - JSON login
   ```bash
   curl -X POST http://localhost:8000/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "user", "password": "pass"}'
   ```

## Common Issues and Solutions

1. **OpenAI API Issues**
   - Check API key in .env
   - Verify API quota
   - Check network connectivity

2. **Database Connection**
   - Verify DATABASE_URL
   - Check database service
   - Run migrations

3. **Performance Issues**
   - Check system resources
   - Monitor API rate limits
   - Review cache settings

## Monitoring and Logs

### Log Files
- Application: `logs/app.log`
- Query Processing: `logs/query_processing.log`
- Errors: `logs/error.log`

### Monitoring Commands
```bash
# View live logs
tail -f logs/query_processing.log

# Check error logs
grep ERROR logs/error.log

# Monitor system resources
top -pid $(pgrep -f "python.*app.main")
```

## Development Guidelines

1. **Adding New Patterns**
   - Add to `QUERY_PATTERNS` in q2_assistants.py
   - Include test cases in edge_test.py
   - Update documentation

2. **Testing New Features**
   - Add unit tests
   - Include edge cases
   - Update test documentation

3. **Performance Optimization**
   - Profile before optimization
   - Test with edge cases
   - Monitor memory usage

## Additional Resources

1. **Documentation**
   - `doc/docs4/q2_architecture.md`
   - `doc/docs4/q2_results.md`
   - `doc/docs4/q3_roadmap.md`

2. **External Links**
   - FastAPI Documentation
   - OpenAI API Reference
   - SQLAlchemy Documentation

## Support

For issues and support:
1. Check existing documentation
2. Review common issues section
3. Check error logs
4. Contact development team 