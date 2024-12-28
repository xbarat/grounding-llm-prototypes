"""
Integration tests for the complete data pipeline.
Tests the flow from data ingestion through transformation.
"""

import pytest
import asyncio
import time
from datetime import datetime
import pandas as pd
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from app.utils.platform_fetcher import fetch_platform_data
from app.utils.normalizer import DataNormalizer
from app.utils.pipeline_validator import (
    validate_pipeline_stage,
    ValidationError
)

# Test data and configurations
TEST_F1_DRIVER = "max_verstappen"
TEST_TYPERACER_USER = "test_user"
PERFORMANCE_THRESHOLDS = {
    "ingestion_time": 2.0,  # seconds
    "normalization_time": 1.0,
    "query_processing_time": 3.0,
    "total_pipeline_time": 7.0
}

# Mock API responses
MOCK_F1_RESPONSE = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "raceId": "1",
                    "season": "2024",
                    "round": "1",
                    "date": "2024-03-02",
                    "time": "13:00:00Z",
                    "Circuit": {
                        "circuitId": "albert_park",
                        "circuitName": "Albert Park",
                        "Location": {
                            "locality": "Melbourne",
                            "country": "Australia"
                        }
                    },
                    "Results": [
                        {
                            "Driver": {
                                "driverId": "max_verstappen",
                                "code": "VER",
                                "givenName": "Max",
                                "familyName": "Verstappen"
                            },
                            "Constructor": {
                                "constructorId": "red_bull",
                                "name": "Red Bull Racing",
                                "nationality": "Austrian"
                            },
                            "grid": 1,
                            "position": 1,
                            "points": 25
                        }
                    ]
                }
            ]
        }
    }
}

MOCK_TYPERACER_RESPONSE = {
    "wpm": 75.5,
    "accuracy": 98.5,
    "session_id": "abc123",
    "timestamp": 1647123456,
    "race_type": "practice",
    "text_length": 100
}

class TestPipelineIntegration:
    """Integration tests for the complete data pipeline"""

    @pytest.fixture
    async def mock_f1_api(self):
        """Mock F1 API responses"""
        with patch('app.utils.platform_fetcher.fetch_f1_data') as mock:
            mock.return_value = MOCK_F1_RESPONSE
            yield mock

    @pytest.fixture
    async def mock_typeracer_api(self):
        """Mock TypeRacer API responses"""
        with patch('app.utils.platform_fetcher.fetch_typeracer_data') as mock:
            mock.return_value = MOCK_TYPERACER_RESPONSE
            yield mock

    @pytest.fixture
    async def f1_pipeline_data(self, mock_f1_api):
        """Fixture to provide F1 data through the pipeline"""
        start_time = time.time()
        
        # 1. Data Ingestion
        ingestion_start = time.time()
        raw_data = await fetch_platform_data("f1", TEST_F1_DRIVER, "driver_standings")
        ingestion_time = time.time() - ingestion_start
        
        # 2. Data Normalization
        normalization_start = time.time()
        normalizer = DataNormalizer()
        normalized_data = normalizer.normalize_f1_race_data(raw_data)
        normalization_time = time.time() - normalization_start
        
        total_time = time.time() - start_time
        
        return {
            "raw_data": raw_data,
            "normalized_data": normalized_data,
            "metrics": {
                "ingestion_time": ingestion_time,
                "normalization_time": normalization_time,
                "total_time": total_time
            }
        }

    @pytest.fixture
    async def typeracer_pipeline_data(self, mock_typeracer_api):
        """Fixture to provide TypeRacer data through the pipeline"""
        start_time = time.time()
        
        # 1. Data Ingestion
        ingestion_start = time.time()
        raw_data = await fetch_platform_data("typeracer", TEST_TYPERACER_USER, "user_stats")
        ingestion_time = time.time() - ingestion_start
        
        # 2. Data Normalization
        normalization_start = time.time()
        normalizer = DataNormalizer()
        normalized_data = normalizer.normalize_typeracer_data(raw_data)
        normalization_time = time.time() - normalization_start
        
        total_time = time.time() - start_time
        
        return {
            "raw_data": raw_data,
            "normalized_data": normalized_data,
            "metrics": {
                "ingestion_time": ingestion_time,
                "normalization_time": normalization_time,
                "total_time": total_time
            }
        }

    async def test_f1_complete_pipeline(self, f1_pipeline_data):
        """Test complete F1 data pipeline flow"""
        # 1. Verify data consistency through pipeline stages
        assert isinstance(f1_pipeline_data["raw_data"], dict)
        assert "MRData" in f1_pipeline_data["raw_data"]
        
        normalized_data = f1_pipeline_data["normalized_data"]
        assert "races" in normalized_data
        assert "drivers" in normalized_data
        assert "constructors" in normalized_data
        
        # 2. Verify data types and formats
        for race in normalized_data["races"]:
            assert isinstance(race["race_id"], str)
            assert isinstance(race["season"], int)
            assert isinstance(race["round"], int)
        
        # 3. Check performance metrics
        metrics = f1_pipeline_data["metrics"]
        assert metrics["ingestion_time"] < PERFORMANCE_THRESHOLDS["ingestion_time"]
        assert metrics["normalization_time"] < PERFORMANCE_THRESHOLDS["normalization_time"]
        assert metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]

    async def test_typeracer_complete_pipeline(self, typeracer_pipeline_data):
        """Test complete TypeRacer data pipeline flow"""
        # 1. Verify data consistency through pipeline stages
        assert isinstance(typeracer_pipeline_data["raw_data"], dict)
        assert any(k in typeracer_pipeline_data["raw_data"] for k in ["wpm", "accuracy"])
        
        normalized_data = typeracer_pipeline_data["normalized_data"]
        assert "wpm" in normalized_data
        assert "accuracy" in normalized_data
        assert "session_id" in normalized_data
        
        # 2. Verify data types and formats
        assert isinstance(normalized_data["wpm"], (int, float))
        assert isinstance(normalized_data["accuracy"], (int, float))
        assert isinstance(normalized_data["timestamp"], datetime)
        
        # 3. Check performance metrics
        metrics = typeracer_pipeline_data["metrics"]
        assert metrics["ingestion_time"] < PERFORMANCE_THRESHOLDS["ingestion_time"]
        assert metrics["normalization_time"] < PERFORMANCE_THRESHOLDS["normalization_time"]
        assert metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]

    async def test_cross_platform_data_consistency(self, f1_pipeline_data, typeracer_pipeline_data):
        """Test data consistency across different platforms"""
        # 1. Verify common metadata fields
        f1_data = f1_pipeline_data["normalized_data"]
        typeracer_data = typeracer_pipeline_data["normalized_data"]
        
        # Both should have timestamps
        assert any(isinstance(race.get("date"), datetime) for race in f1_data["races"])
        assert isinstance(typeracer_data["timestamp"], datetime)
        
        # Both should have unique identifiers
        assert all("race_id" in race for race in f1_data["races"])
        assert "session_id" in typeracer_data
        
        # 2. Verify performance metrics consistency
        f1_metrics = f1_pipeline_data["metrics"]
        typeracer_metrics = typeracer_pipeline_data["metrics"]
        
        # Both should meet performance thresholds
        assert f1_metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]
        assert typeracer_metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]

    async def test_pipeline_error_handling(self, mock_f1_api, mock_typeracer_api):
        """Test error handling throughout the pipeline"""
        # 1. Test invalid platform
        with pytest.raises(ValueError, match="Unsupported platform"):
            await fetch_platform_data("invalid_platform", "test_user", "stats")
        
        # 2. Test invalid endpoint
        mock_f1_api.side_effect = ValueError("Unknown F1 endpoint: invalid_endpoint")
        with pytest.raises(ValueError, match="Unknown F1 endpoint"):
            await fetch_platform_data("f1", TEST_F1_DRIVER, "invalid_endpoint")
        mock_f1_api.side_effect = None  # Reset side effect
        
        # 3. Test invalid F1 data validation at ingestion
        invalid_f1_data = {
            "invalid": "data"
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', invalid_f1_data, platform='f1')
        
        # 4. Test invalid TypeRacer data validation at ingestion
        invalid_typeracer_data = {
            "invalid": "data"
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('ingestion', invalid_typeracer_data, platform='typeracer')
        
        # 5. Test missing required fields in normalized data
        incomplete_normalized_data = {
            "races": []  # Missing other required fields
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('normalization', incomplete_normalized_data, platform='f1')
        
        # 6. Test invalid data types in normalized data
        invalid_normalized_data = {
            "wpm": "not a number",
            "accuracy": "not a number",
            "session_id": 123  # Should be string
        }
        with pytest.raises(ValidationError):
            validate_pipeline_stage('normalization', invalid_normalized_data, platform='typeracer')
        
        # 7. Test invalid query
        with pytest.raises(ValidationError):
            validate_pipeline_stage('query', "", platform='f1')
        
        # 8. Test invalid DataFrame
        invalid_df = pd.DataFrame()  # Empty DataFrame
        with pytest.raises(ValidationError):
            validate_pipeline_stage(
                'transformation',
                invalid_df,
                platform='f1',
                required_columns=['driver_id', 'race_id']
            )

    async def test_pipeline_data_transformation(self, f1_pipeline_data):
        """Test data transformation stage"""
        normalized_data = f1_pipeline_data["normalized_data"]
        
        # Create DataFrame from normalized data
        df = pd.DataFrame(normalized_data["race_results"])
        
        # 1. Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "driver_id" in df.columns
        assert "race_id" in df.columns
        
        # 2. Verify data types
        assert df["points"].dtype in ["int64", "float64"]
        assert df["position"].dtype in ["int64", "float64"]
        
        # 3. Verify no duplicate race-driver combinations
        assert not df.duplicated(subset=["race_id", "driver_id"]).any()
        
        # 4. Verify performance metrics
        metrics = f1_pipeline_data["metrics"]
        assert metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]

    async def test_pipeline_data_quality(self, f1_pipeline_data, typeracer_pipeline_data):
        """Test data quality throughout the pipeline"""
        # 1. Check F1 data quality
        f1_data = f1_pipeline_data["normalized_data"]
        
        # Verify no missing race IDs
        assert all("race_id" in race for race in f1_data["races"])
        
        # Verify valid positions and points
        for result in f1_data["race_results"]:
            assert isinstance(result["position"], (int, type(None)))
            assert isinstance(result["points"], (int, float))
            assert result["points"] >= 0
        
        # 2. Check TypeRacer data quality
        tr_data = typeracer_pipeline_data["normalized_data"]
        
        # Verify valid WPM and accuracy
        assert isinstance(tr_data["wpm"], (int, float))
        assert tr_data["wpm"] >= 0
        assert isinstance(tr_data["accuracy"], (int, float))
        assert 0 <= tr_data["accuracy"] <= 100

    @pytest.mark.performance
    async def test_pipeline_performance_metrics(self, f1_pipeline_data, typeracer_pipeline_data):
        """Test detailed performance metrics of the pipeline"""
        # 1. F1 Pipeline Performance
        f1_metrics = f1_pipeline_data["metrics"]
        assert f1_metrics["ingestion_time"] < PERFORMANCE_THRESHOLDS["ingestion_time"]
        assert f1_metrics["normalization_time"] < PERFORMANCE_THRESHOLDS["normalization_time"]
        assert f1_metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]
        
        # 2. TypeRacer Pipeline Performance
        tr_metrics = typeracer_pipeline_data["metrics"]
        assert tr_metrics["ingestion_time"] < PERFORMANCE_THRESHOLDS["ingestion_time"]
        assert tr_metrics["normalization_time"] < PERFORMANCE_THRESHOLDS["normalization_time"]
        assert tr_metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"]
        
        # 3. Log performance metrics
        print(f"\nPerformance Metrics:")
        print(f"F1 Pipeline: {f1_metrics}")
        print(f"TypeRacer Pipeline: {tr_metrics}")
        
        # 4. Verify relative performance
        assert abs(f1_metrics["ingestion_time"] - tr_metrics["ingestion_time"]) < 1.0  # Should be within 1 second
        assert abs(f1_metrics["total_time"] - tr_metrics["total_time"]) < 2.0  # Should be within 2 seconds 

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_real_f1_data_pipeline(self):
        """Test pipeline with real F1 API data for Max Verstappen's latest race"""
        start_time = time.time()
        
        # 1. Data Ingestion
        ingestion_start = time.time()
        raw_data = await fetch_platform_data("f1", "max_verstappen", "driver_standings")
        ingestion_time = time.time() - ingestion_start
        
        # 2. Data Normalization
        normalization_start = time.time()
        normalizer = DataNormalizer()
        normalized_data = normalizer.normalize_f1_standings_data(raw_data)  # Use standings normalizer
        normalization_time = time.time() - normalization_start
        
        total_time = time.time() - start_time
        
        # Log raw data for inspection
        print("\nReal F1 API Response:")
        print(f"Raw data: {raw_data}")
        print(f"\nNormalized data: {normalized_data}")
        
        # Verify data structure
        assert isinstance(raw_data, dict)
        assert "MRData" in raw_data
        assert "StandingsTable" in raw_data["MRData"]
        
        # Verify normalized data
        assert "drivers" in normalized_data
        assert "constructors" in normalized_data
        assert "driver_standings" in normalized_data
        
        # Verify Max Verstappen's data is present
        drivers = normalized_data.get("drivers", [])
        max_found = any(
            driver.get("driver_id") == "max_verstappen" 
            for driver in drivers
        )
        assert max_found, "Max Verstappen's data not found in response"
        
        # Verify Max's standings data
        standings = normalized_data.get("driver_standings", [])
        max_standing = next(
            (s for s in standings if s.get("driver_id") == "max_verstappen"),
            None
        )
        assert max_standing is not None, "Max Verstappen's standings not found"
        assert isinstance(max_standing.get("points"), (int, float))
        assert isinstance(max_standing.get("position"), int)
        assert isinstance(max_standing.get("wins"), int)
        
        # Verify performance
        metrics = {
            "ingestion_time": ingestion_time,
            "normalization_time": normalization_time,
            "total_time": total_time
        }
        print(f"\nReal API Performance Metrics:")
        print(f"Metrics: {metrics}")
        
        assert metrics["ingestion_time"] < PERFORMANCE_THRESHOLDS["ingestion_time"]
        assert metrics["normalization_time"] < PERFORMANCE_THRESHOLDS["normalization_time"]
        assert metrics["total_time"] < PERFORMANCE_THRESHOLDS["total_pipeline_time"] 