import unittest
import asyncio
import pandas as pd
from app.pipeline.data2 import DataPipeline, DataTransformer, DataResponse
from app.query.processor import DataRequirements
import pytest

class TestDataPipeline(unittest.TestCase):
    """Test the F1 data pipeline with the new mappings"""
    
    def setUp(self):
        self.pipeline = DataPipeline()
        self.transformer = DataTransformer()
        
        # Test cases for different query types
        self.test_cases = [
            {
                "name": "Single Driver Results",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2023", "driver": "max verstappen"}
                ),
                "expected_columns": ["race", "season", "driver", "position", "points"]
            },
            {
                "name": "Historical Driver Results",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2012", "driver": "michael schumacher"}
                ),
                "expected_columns": ["race", "season", "driver", "position", "points"]
            },
            {
                "name": "Driver with Special Characters",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2023", "driver": "M. Schumacher"}
                ),
                "expected_columns": ["race", "season", "driver", "position", "points"]
            },
            {
                "name": "Driver with Abbreviation",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2023", "driver": "VER"}
                ),
                "expected_columns": ["race", "season", "driver", "position", "points"]
            }
        ]

    @pytest.mark.asyncio
    async def test_data_retrieval(self):
        """Test data retrieval for different driver formats"""
        for case in self.test_cases:
            with self.subTest(case["name"]):
                response = await self.pipeline.process(case["requirements"])
                
                # Check if the request was successful
                self.assertTrue(response.success, f"Failed to retrieve data for {case['name']}")
                self.assertIsNotNone(response.data, f"No data returned for {case['name']}")
                
                if response.data:
                    df = response.data["results"]
                    # Check DataFrame structure
                    self.assertIsInstance(df, pd.DataFrame)
                    self.assertFalse(df.empty, f"Empty DataFrame for {case['name']}")
                    
                    # Verify required columns are present
                    for col in case["expected_columns"]:
                        self.assertIn(col, df.columns, f"Missing column {col} in {case['name']}")
                    
                    # Check data quality
                    self.assertFalse(df["driver"].isna().any(), "Found null driver names")
                    self.assertFalse(df["position"].isna().all(), "All positions are null")

    @pytest.mark.asyncio
    async def test_driver_variations(self):
        """Test that different variations of driver names return consistent results"""
        variations = [
            ("max verstappen", "max_verstappen"),
            ("verstappen", "max_verstappen"),
            ("VER", "max_verstappen"),
            ("M Verstappen", "max_verstappen")
        ]
        
        base_requirements = DataRequirements(
            endpoint="/api/f1/drivers",
            params={"season": "2023"}
        )
        
        base_response = None
        for driver_input, expected_id in variations:
            with self.subTest(f"Testing variation: {driver_input}"):
                requirements = DataRequirements(
                    endpoint=base_requirements.endpoint,
                    params={**base_requirements.params, "driver": driver_input}
                )
                
                response = await self.pipeline.process(requirements)
                self.assertTrue(response.success, f"Failed to retrieve data for {driver_input}")
                
                if base_response is None:
                    base_response = response
                else:
                    # Compare with base response
                    if response.data and base_response.data:
                        self.assertEqual(
                            response.data["results"].shape,
                            base_response.data["results"].shape,
                            f"Inconsistent results for {driver_input}"
                        )

    @pytest.mark.asyncio
    async def test_historical_data(self):
        """Test retrieval of historical F1 data"""
        historical_drivers = [
            ("michael schumacher", "2004"),
            ("ayrton senna", "1991"),
            ("alain prost", "1989")
        ]
        
        for driver, season in historical_drivers:
            with self.subTest(f"Testing {driver} in {season}"):
                requirements = DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": season, "driver": driver}
                )
                
                response = await self.pipeline.process(requirements)
                self.assertTrue(response.success, f"Failed to retrieve data for {driver} in {season}")
                
                if response.data:
                    df = response.data["results"]
                    self.assertFalse(df.empty, f"Empty DataFrame for {driver} in {season}")
                    self.assertEqual(df["season"].iloc[0], season)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid inputs"""
        invalid_cases = [
            {
                "name": "Invalid Driver",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2023", "driver": "nonexistent_driver"}
                )
            },
            {
                "name": "Invalid Season",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "9999", "driver": "max verstappen"}
                )
            },
            {
                "name": "Empty Driver",
                "requirements": DataRequirements(
                    endpoint="/api/f1/drivers",
                    params={"season": "2023", "driver": ""}
                )
            }
        ]
        
        for case in invalid_cases:
            with self.subTest(case["name"]):
                response = await self.pipeline.process(case["requirements"])
                # Should either return empty DataFrame or error message
                if response.success:
                    self.assertTrue(
                        response.data["results"].empty,
                        f"Expected empty DataFrame for {case['name']}"
                    )
                else:
                    self.assertIsNotNone(response.error)

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

if __name__ == '__main__':
    unittest.main() 