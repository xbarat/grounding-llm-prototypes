"""
Tests for the data pipeline validation module.
"""

import pytest
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.pipeline_validator import (
    validate_pipeline_stage,
    RawDataValidator,
    NormalizedDataValidator,
    QueryValidator,
    DataFrameValidator,
    ValidationError
)
import pandas as pd

# Test data
VALID_F1_RAW_DATA = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "raceId": "1",
                    "season": "2024",
                    "round": "1",
                    "Circuit": {
                        "circuitId": "albert_park",
                        "circuitName": "Albert Park",
                        "Location": {
                            "locality": "Melbourne",
                            "country": "Australia"
                        }
                    }
                }
            ]
        }
    }
}

VALID_TYPERACER_RAW_DATA = {
    "wpm": 75.5,
    "accuracy": 98.5,
    "session_id": "abc123",
    "timestamp": 1647123456
}

VALID_F1_NORMALIZED_DATA = {
    "races": [
        {
            "race_id": "1",
            "season": 2024,
            "round": 1,
            "circuit_id": "albert_park"
        }
    ],
    "circuits": [
        {
            "circuit_id": "albert_park",
            "name": "Albert Park",
            "location": "Melbourne",
            "country": "Australia"
        }
    ],
    "drivers": [],
    "constructors": []
}

VALID_TYPERACER_NORMALIZED_DATA = {
    "wpm": 75.5,
    "accuracy": 98.5,
    "session_id": "abc123",
    "timestamp": datetime.fromtimestamp(1647123456),
    "race_type": "practice",
    "text_length": 0
}

# Stage 1: Data Ingestion Tests
class TestDataIngestion:
    """Test suite for data ingestion stage"""

    def test_valid_f1_raw_data(self):
        """Test valid F1 raw data ingestion"""
        assert validate_pipeline_stage('ingestion', VALID_F1_RAW_DATA, platform='f1')

    def test_valid_typeracer_raw_data(self):
        """Test valid TypeRacer raw data ingestion"""
        assert validate_pipeline_stage('ingestion', VALID_TYPERACER_RAW_DATA, platform='typeracer')

    def test_invalid_f1_data_structure(self):
        """Test F1 data with invalid structure"""
        invalid_data = {"MRData": {}}  # Missing RaceTable
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', invalid_data, platform='f1')

    def test_invalid_typeracer_data_structure(self):
        """Test TypeRacer data with invalid structure"""
        invalid_data = {"speed": 75.5}  # Using wrong field name
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', invalid_data, platform='typeracer')

    def test_empty_data(self):
        """Test empty data object"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', {}, platform='f1')

    def test_none_data(self):
        """Test None data"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', None, platform='f1')

    def test_invalid_platform(self):
        """Test invalid platform"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', VALID_F1_RAW_DATA, platform='invalid')

# Stage 2: Data Normalization Tests
class TestDataNormalization:
    """Test suite for data normalization stage"""

    def test_valid_f1_normalized_data(self):
        """Test valid F1 normalized data"""
        assert validate_pipeline_stage('normalization', VALID_F1_NORMALIZED_DATA, platform='f1')

    def test_valid_typeracer_normalized_data(self):
        """Test valid TypeRacer normalized data"""
        assert validate_pipeline_stage('normalization', VALID_TYPERACER_NORMALIZED_DATA, platform='typeracer')

    def test_missing_required_f1_fields(self):
        """Test F1 data missing required fields"""
        invalid_data = {
            "races": [],
            "circuits": []  # Missing drivers and constructors
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('normalization', invalid_data, platform='f1')

    def test_missing_required_typeracer_fields(self):
        """Test TypeRacer data missing required fields"""
        invalid_data = {
            "wpm": 75.5,
            # Missing accuracy and session_id
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('normalization', invalid_data, platform='typeracer')

    def test_invalid_data_types(self):
        """Test data with invalid types"""
        invalid_data = {
            "wpm": "75.5",  # String instead of float
            "accuracy": "98.5",
            "session_id": 123  # Number instead of string
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('normalization', invalid_data, platform='typeracer')

# Stage 3: Query Processing Tests
class TestQueryProcessing:
    """Test suite for query processing stage"""

    def test_valid_query(self):
        """Test valid query"""
        assert validate_pipeline_stage(
            'query',
            "Show driver performance trend",
            platform='f1',
            parameters={"driver_id": "max_verstappen"}
        )

    def test_empty_query(self):
        """Test empty query"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage('query', "", platform='f1')

    def test_none_query(self):
        """Test None query"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage('query', None, platform='f1')

    def test_query_without_parameters(self):
        """Test query without parameters"""
        assert validate_pipeline_stage(
            'query',
            "Show overall race statistics",
            platform='f1'
        )

    def test_query_with_invalid_parameters(self):
        """Test query with invalid parameters"""
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'query',
                "Show driver performance",
                platform='f1',
                parameters=["invalid", "parameter", "type"]  # List instead of dict
            )

# Stage 4: Data Transformation Tests
class TestDataTransformation:
    """Test suite for data transformation stage"""

    def test_valid_dataframe(self):
        """Test valid DataFrame"""
        df = pd.DataFrame({
            'driver_id': ['max_verstappen', 'lewis_hamilton'],
            'points': [25, 18],
            'position': [1, 2]
        })
        assert validate_pipeline_stage(
            'transformation',
            df,
            platform='f1',
            required_columns=['driver_id', 'points', 'position']
        )

    def test_missing_columns(self):
        """Test DataFrame with missing columns"""
        df = pd.DataFrame({
            'driver_id': ['max_verstappen', 'lewis_hamilton']
        })
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                df,
                platform='f1',
                required_columns=['driver_id', 'points', 'position']
            )

    def test_empty_dataframe(self):
        """Test empty DataFrame"""
        df = pd.DataFrame()
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                df,
                platform='f1',
                required_columns=['driver_id']
            )

    def test_null_values(self):
        """Test DataFrame with null values"""
        df = pd.DataFrame({
            'driver_id': ['max_verstappen', None],
            'points': [25, 18],
            'position': [1, 2]
        })
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                df,
                platform='f1',
                required_columns=['driver_id', 'points', 'position'],
                allow_nulls=False
            )

    def test_allow_null_values(self):
        """Test DataFrame with allowed null values"""
        df = pd.DataFrame({
            'driver_id': ['max_verstappen', None],
            'points': [25, 18],
            'position': [1, 2]
        })
        assert validate_pipeline_stage(
            'transformation',
            df,
            platform='f1',
            required_columns=['driver_id', 'points', 'position'],
            allow_nulls=True
        )

    def test_minimum_rows(self):
        """Test DataFrame minimum rows requirement"""
        df = pd.DataFrame({
            'driver_id': ['max_verstappen'],
            'points': [25],
            'position': [1]
        })
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                df,
                platform='f1',
                required_columns=['driver_id', 'points', 'position'],
                min_rows=2
            )

    def test_invalid_dataframe_type(self):
        """Test invalid DataFrame type"""
        not_a_df = [
            {'driver_id': 'max_verstappen', 'points': 25, 'position': 1},
            {'driver_id': 'lewis_hamilton', 'points': 18, 'position': 2}
        ]
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                not_a_df,
                platform='f1',
                required_columns=['driver_id', 'points', 'position']
            ) 