"""Configuration settings for F1 API integration tests"""

# API Configuration
API_CONFIG = {
    "base_url": "http://ergast.com/api/f1",
    "rate_limit": 4,  # requests per second
    "timeout": 10,    # seconds
    "retries": 3      # number of retries for failed requests
}

# Test Data Configuration
TEST_DATA = {
    "current_season": "2024",
    "test_driver_id": "max_verstappen",
    "test_constructor_id": "red_bull",
    "test_circuit_id": "monza",
    "rounds_to_test": 5  # number of rounds to include in analysis tests
}

# Required Fields for Validation
REQUIRED_FIELDS = {
    "race": ["season", "round", "raceName", "Circuit", "date", "time"],
    "driver": ["driverId", "givenName", "familyName", "nationality"],
    "constructor": ["constructorId", "name", "nationality"],
    "circuit": ["circuitId", "circuitName", "Location"],
    "result": ["position", "points", "Driver", "Constructor", "grid", "laps", "status"],
    "qualifying": ["position", "Driver", "Constructor", "Q1"],
    "standings": ["position", "points", "wins"]
}

# Analysis Queries for Testing
TEST_QUERIES = [
    "Show the relationship between grid position and race finish position",
    "Compare points scored by each constructor across races",
    "Analyze qualifying performance vs race performance",
    "Show driver performance trends over the season",
    "Compare teammate qualifying battles"
]

# Visualization Types to Test
VISUALIZATION_TYPES = [
    "line_chart",     # For trends over time
    "bar_chart",      # For comparisons
    "scatter_plot",   # For correlations
    "box_plot",       # For distributions
    "heat_map",       # For performance matrices
    "radar_chart"     # For driver/team comparisons
]

# Sample Data Structure
SAMPLE_RACE_RESULT = {
    "race": "British Grand Prix",
    "driver": "Max Verstappen",
    "constructor": "Red Bull",
    "position": 1,
    "points": 25,
    "grid": 1,
    "laps": 52,
    "status": "Finished",
    "time": "1:27:38.241"
}

# Error Messages
ERROR_MESSAGES = {
    "api_error": "Failed to fetch data from F1 API: {error}",
    "validation_error": "Data validation failed: {error}",
    "rate_limit": "Rate limit exceeded. Please wait before making more requests.",
    "missing_data": "Required data not found in API response: {field}",
    "analysis_error": "Failed to perform analysis: {error}"
}

# Cache Configuration
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # Time to live in seconds
    "max_size": 100  # Maximum number of items to cache
} 