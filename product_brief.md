
## Files

**Essential Core Files:**
backend/app/main.py - Main application entry point
backend/app/pipeline/data2.py - Core data processing logic
backend/app/pipeline/mappings.py - Driver and circuit mappings
backend/app/query/processor.py - Query processing logic
backend/app/analyst/prompts.py - Code generation prompts
backend/app/analyst/generate.py - Code generation logic

**Essential Test Files:**
backend/app/pipeline/test_pipeline2.py - Main test suite
backend/app/pipeline/test_endpoints.py - API endpoint validation

**Helper Files:**
backend/app/pipeline/data_validator.py - Data validation utilities
backend/app/analyst/variable_mapper.py - Variable mapping utilities
backend/app/analyst/plotting.py - Plotting utilities

## File structure

backend/app/
├── main.py
├── pipeline/
│   ├── data2.py
│   ├── mappings.py
│   ├── data_validator.py
│   ├── test_pipeline2.py
│   ├── test_endpoints.py
│   └── __init__.py
├── query/
│   ├── processor.py
│   └── __init__.py
└── analyst/
    ├── generate.py
    ├── prompts.py
    ├── plotting.py
    ├── variable_mapper.py
    └── __init__.py