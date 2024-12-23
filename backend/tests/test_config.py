"""Configuration settings for integration tests"""

# API Configuration
API_CONFIG = {
    "base_url": "http://ergast.com/api/f1",
    "rate_limit": 4,  # requests per second
    "timeout": 10,  # seconds
    "retries": 3
}

# Test Data Configuration
TEST_DATA = {
    "year": 2024,
    "num_races": 23,
    "num_drivers": 20,
    "rounds_to_test": 5
}

# Required Fields for Validation
REQUIRED_FIELDS = {
    "race": [
        "season",
        "round",
        "raceName",
        "Circuit",
        "date",
        "time"
    ],
    "circuit": [
        "circuitId",
        "circuitName",
        "Location"
    ],
    "driver": [
        "driverId",
        "code",
        "givenName",
        "familyName",
        "nationality"
    ],
    "constructor": [
        "constructorId",
        "name",
        "nationality"
    ],
    "result": [
        "position",
        "points",
        "Driver",
        "Constructor",
        "grid",
        "status"
    ],
    "qualifying": [
        "position",
        "Driver",
        "Constructor",
        "Q1"
    ]
}

# Error Messages
ERROR_MESSAGES = {
    "api_error": "API request failed: {error}",
    "missing_data": "Data validation failed: {field}",
    "analysis_error": "Analysis failed: {error}",
    "visualization_error": "Visualization failed: {error}"
}

# Cache Configuration
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # 1 hour
    "max_size": 1000  # number of items
}

# Test Queries
TEST_QUERIES = [
    "Compare the performance of top 3 drivers across all races",
    "Analyze the correlation between grid position and race finish position",
    "Calculate average points per race for each constructor",
    "Find races with the most overtakes from starting position",
    "Identify drivers with the best qualifying performance"
]

# Visualization Types
VISUALIZATION_TYPES = [
    "line_chart",
    "bar_chart",
    "scatter_plot",
    "box_plot",
    "heat_map"
] 