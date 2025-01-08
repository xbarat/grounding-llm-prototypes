# F1 Data Analysis System - High Level Architecture

## Core Components

### 1. Data Pipeline (`pipeline/`)
- **Data Transformer** (`data2.py`): Core data processing and transformation logic
- **Mappings** (`mappings.py`): Centralized ID mapping system for drivers and circuits
- **Validation** (`data_validator.py`): Data quality validation and verification
- **Tests**: Comprehensive test suite for pipeline validation

### 2. Query Processing (`query/`)
- **Query Processor** (`processor.py`): Natural language query interpretation and requirement extraction
- Focus on time-series analysis queries for multi-season trends

### 3. Analysis Engine (`analyst/`)
- **Code Generation** (`generate.py`, `prompts.py`): Dynamic analysis code generation
- **Visualization** (`plotting.py`): Time-series focused plotting utilities
- **Variable Mapping** (`variable_mapper.py`): Data field standardization

## Data Flow
1. User Query → Query Processor → Data Requirements
2. Requirements → Data Pipeline → Normalized DataFrames
3. DataFrames → Analysis Engine → Visualizations

## Key Features
- Robust driver/circuit ID mapping system
- Time-series focused data analysis
- Standardized data validation
- Dynamic code generation for analysis
- Comprehensive test coverage

## Design Decisions
1. Centralized mapping system for consistent ID handling
2. Focus on time-series analysis over single-race statistics
3. Standardized DataFrame structure for consistent analysis
4. Robust error handling and data validation
5. Clear separation of concerns between components

