"""Test fixtures for the main application."""
import pytest
from datetime import datetime
import pandas as pd

@pytest.fixture
def sample_query():
    """Valid F1 query for testing."""
    return "Show Ferrari's performance in 2023"

@pytest.fixture
def empty_query():
    """Empty query for testing."""
    return ""

@pytest.fixture
def invalid_query():
    """Invalid query for testing."""
    return "   "

@pytest.fixture
def pipeline_error_query():
    """Query that should trigger pipeline error."""
    return "Invalid query that will cause pipeline error"

@pytest.fixture
def no_data_query():
    """Query that should return no data."""
    return "Show results for nonexistent team"

@pytest.fixture
def code_error_query():
    """Query that should generate invalid code."""
    return "Generate invalid analysis code"

@pytest.fixture
def sample_pipeline_result():
    """Sample successful pipeline result."""
    return {
        'success': True,
        'data': {
            'results': [
                {
                    'constructor_id': 'ferrari',
                    'year': 2023,
                    'points': 406,
                    'position': 3,
                    'wins': 1
                }
            ]
        },
        'metadata': {
            'query_type': 'historical',
            'timestamp': datetime.now().isoformat(),
            'years_processed': 1
        },
        'error': None
    }

@pytest.fixture
def empty_pipeline_result():
    """Pipeline result with no data."""
    return {
        'success': True,
        'data': {
            'results': []
        },
        'metadata': {
            'query_type': 'historical',
            'timestamp': datetime.now().isoformat()
        },
        'error': None
    }

@pytest.fixture
def error_pipeline_result():
    """Failed pipeline result."""
    return {
        'success': False,
        'data': None,
        'metadata': {
            'timestamp': datetime.now().isoformat()
        },
        'error': 'Pipeline processing failed'
    } 