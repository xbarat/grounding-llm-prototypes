"""
Test module for verifying the complete data pipeline.

This module tests the end-to-end flow of data from input to output,
including platform selection, data fetching, and normalization.
"""

import pytest
from httpx import AsyncClient
import json
from app.utils.platform_fetcher import fetch_platform_data
from app.utils.f1_api import F1API
from app.routes.platforms import SUPPORTED_PLATFORMS

@pytest.mark.asyncio
async def test_typeracer_pipeline():
    """Test the complete pipeline for TypeRacer data."""
    # Test data
    platform = "typeracer"
    identifier = "test_user"  # Replace with a known TypeRacer username for integration testing
    endpoint = "user_stats"

    try:
        # Fetch data
        data = await fetch_platform_data(platform, identifier, endpoint)
        
        # Verify data structure
        assert isinstance(data, dict), "Data should be a dictionary"
        assert "races" in data or "results" in data, "Data should contain race information"
        
        # Log the data structure for debugging
        print(f"\nTypeRacer Data Structure:\n{json.dumps(data, indent=2)}")
        
        return True
    except Exception as e:
        print(f"TypeRacer pipeline error: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_f1_pipeline():
    """Test the complete pipeline for F1 data."""
    # Test data
    platform = "f1"
    identifier = "max_verstappen"  # Using a known driver ID
    endpoint = "driver_results"

    try:
        # Fetch data
        data = await fetch_platform_data(platform, identifier, endpoint)
        
        # Verify data structure
        assert isinstance(data, dict), "Data should be a dictionary"
        assert "MRData" in data, "F1 data should contain MRData"
        
        # Log the data structure for debugging
        print(f"\nF1 Data Structure:\n{json.dumps(data, indent=2)}")
        
        return True
    except Exception as e:
        print(f"F1 pipeline error: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_platform_validation():
    """Test platform validation in the pipeline."""
    # Test invalid platform
    with pytest.raises(ValueError):
        await fetch_platform_data("invalid_platform", "test_user", "stats")

@pytest.mark.asyncio
async def test_endpoint_validation():
    """Test endpoint validation in the pipeline."""
    # Test invalid endpoint for F1
    with pytest.raises(ValueError):
        await fetch_platform_data("f1", "max_verstappen", "invalid_endpoint")

@pytest.mark.asyncio
async def test_supported_platforms():
    """Test that all supported platforms are properly configured."""
    for platform in SUPPORTED_PLATFORMS:
        assert platform.id in ["typeracer", "f1"], f"Unsupported platform: {platform.id}"
        assert platform.identifier_type, f"Missing identifier type for {platform.id}"
        assert platform.example_identifier, f"Missing example identifier for {platform.id}"

@pytest.mark.asyncio
async def test_f1_specific_endpoints():
    """Test F1-specific endpoints in the pipeline."""
    async with F1API() as f1_api:
        # Test driver standings
        standings = await f1_api.fetch_driver_standings()
        assert "MRData" in standings, "Driver standings should contain MRData"
        
        # Test race results
        results = await f1_api.fetch_race_results()
        assert "MRData" in results, "Race results should contain MRData"
        
        # Test qualifying results
        qualifying = await f1_api.fetch_qualifying_results()
        assert "MRData" in qualifying, "Qualifying results should contain MRData"

if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        """Run all pipeline tests."""
        print("\nTesting TypeRacer Pipeline...")
        typeracer_result = await test_typeracer_pipeline()
        print(f"TypeRacer Pipeline Test: {'✅ Passed' if typeracer_result else '❌ Failed'}")
        
        print("\nTesting F1 Pipeline...")
        f1_result = await test_f1_pipeline()
        print(f"F1 Pipeline Test: {'✅ Passed' if f1_result else '❌ Failed'}")
        
        print("\nTesting Platform Validation...")
        try:
            await test_platform_validation()
            print("Platform Validation Test: ✅ Passed")
        except Exception as e:
            print(f"Platform Validation Test: ❌ Failed - {str(e)}")
        
        print("\nTesting Endpoint Validation...")
        try:
            await test_endpoint_validation()
            print("Endpoint Validation Test: ✅ Passed")
        except Exception as e:
            print(f"Endpoint Validation Test: ❌ Failed - {str(e)}")
        
        print("\nTesting Supported Platforms...")
        try:
            await test_supported_platforms()
            print("Supported Platforms Test: ✅ Passed")
        except Exception as e:
            print(f"Supported Platforms Test: ❌ Failed - {str(e)}")
        
        print("\nTesting F1 Specific Endpoints...")
        try:
            await test_f1_specific_endpoints()
            print("F1 Specific Endpoints Test: ✅ Passed")
        except Exception as e:
            print(f"F1 Specific Endpoints Test: ❌ Failed - {str(e)}")

    # Run the tests
    asyncio.run(run_tests()) 