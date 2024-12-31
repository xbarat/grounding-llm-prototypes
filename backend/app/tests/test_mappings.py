import unittest
import httpx
import asyncio
from app.pipeline.mappings import (
    DRIVER_IDS,
    DRIVER_DISPLAY_TO_API,
    get_driver_api_id,
    normalize_driver_id,
    build_url
)

class TestDriverMappings(unittest.TestCase):
    """Test driver ID mappings and URL construction"""
    
    def setUp(self):
        self.base_url = "http://ergast.com/api/f1"
        
        # Current drivers
        self.current_drivers = [
            ("max verstappen", "max_verstappen"),
            ("lewis hamilton", "hamilton"),
            ("charles leclerc", "leclerc"),
            ("carlos sainz", "carlos_sainz_jr"),
            ("oscar piastri", "piastri"),
            ("lando norris", "norris"),
            ("george russell", "russell"),
            ("fernando alonso", "alonso")
        ]
        
        # Historical drivers with known API IDs
        self.historical_drivers = [
            ("michael schumacher", "michael_schumacher"),
            ("ayrton senna", "senna"),
            ("alain prost", "prost"),
            ("niki lauda", "lauda"),
            ("juan manuel fangio", "fangio"),
            ("jim clark", "clark"),
            ("jackie stewart", "stewart"),
            ("nelson piquet", "piquet")
        ]
        
        # Edge cases and variations
        self.edge_cases = [
            ("M. Schumacher", "michael_schumacher"),
            ("Schumi", "michael_schumacher"),
            ("MSC", "michael_schumacher"),
            ("VER", "max_verstappen"),
            ("HAM", "hamilton"),
            ("LEC", "leclerc")
        ]
        
        # Random historical drivers to test API robustness
        self.random_drivers = [
            "jack brabham",
            "graham hill",
            "emerson fittipaldi",
            "james hunt",
            "mario andretti",
            "gilles villeneuve",
            "keke rosberg",
            "nigel mansell",
            "damon hill",
            "mika hakkinen"
        ]

    async def validate_driver_endpoint(self, driver_id: str) -> bool:
        """Test if a driver endpoint is valid by making a real API call"""
        url = f"{self.base_url}/drivers/{driver_id}/results.json"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if "MRData" in data:
                        return True
                return False
            except Exception as e:
                print(f"Error validating endpoint for {driver_id}: {str(e)}")
                return False

    def test_current_driver_normalization(self):
        """Test that current driver IDs are normalized consistently"""
        for display_name, expected_api_id in self.current_drivers:
            normalized = normalize_driver_id(display_name)
            api_id = get_driver_api_id(normalized)
            self.assertEqual(api_id, expected_api_id)

    def test_historical_driver_normalization(self):
        """Test that historical driver IDs are normalized consistently"""
        for display_name, expected_api_id in self.historical_drivers:
            normalized = normalize_driver_id(display_name)
            api_id = get_driver_api_id(normalized)
            self.assertEqual(api_id, expected_api_id)

    def test_edge_cases(self):
        """Test edge cases and variations in driver names"""
        for input_name, expected_api_id in self.edge_cases:
            normalized = normalize_driver_id(input_name)
            api_id = get_driver_api_id(normalized)
            self.assertEqual(api_id, expected_api_id)

    def test_random_historical_drivers(self):
        """Test that random historical drivers return valid API IDs"""
        for driver_name in self.random_drivers:
            normalized = normalize_driver_id(driver_name)
            api_id = get_driver_api_id(normalized)
            self.assertTrue(isinstance(api_id, str) and len(api_id) > 0)
            # Validate that the API accepts this ID
            result = asyncio.run(self.validate_driver_endpoint(api_id))
            self.assertTrue(result, f"API endpoint failed for driver: {driver_name} -> {api_id}")

    def test_driver_id_case_insensitivity(self):
        """Test that driver ID mapping is case insensitive"""
        test_cases = [
            "MAX VERSTAPPEN",
            "Max Verstappen",
            "max verstappen",
            "mAx vErStApPeN",
            "LEWIS HAMILTON",
            "LeWiS hAmIlToN",
            "MICHAEL SCHUMACHER",
            "MiChAeL sChUmAcHeR"
        ]
        expected_results = {
            "max verstappen": "max_verstappen",
            "lewis hamilton": "hamilton",
            "michael schumacher": "michael_schumacher"
        }
        
        for test_case in test_cases:
            normalized = normalize_driver_id(test_case)
            api_id = get_driver_api_id(normalized)
            base_name = normalize_driver_id(test_case)
            self.assertEqual(api_id, expected_results[base_name])

    def test_driver_id_space_handling(self):
        """Test that spaces and special characters are handled consistently"""
        test_cases = [
            ("lewis hamilton", "hamilton"),
            ("lewis_hamilton", "hamilton"),
            ("lewis  hamilton", "hamilton"),
            (" lewis hamilton ", "hamilton"),
            ("max.verstappen", "max_verstappen"),
            ("max-verstappen", "max_verstappen"),
            ("max   verstappen", "max_verstappen")
        ]
        
        for input_name, expected_api_id in test_cases:
            normalized = normalize_driver_id(input_name)
            api_id = get_driver_api_id(normalized)
            self.assertEqual(api_id, expected_api_id)

    def test_api_endpoint_validation(self):
        """Test that all driver IDs work with the actual API"""
        # Test both current and historical drivers
        all_drivers = self.current_drivers + self.historical_drivers
        for _, api_id in all_drivers:
            result = asyncio.run(self.validate_driver_endpoint(api_id))
            self.assertTrue(result, f"API endpoint failed for driver ID: {api_id}")

    def test_url_construction(self):
        """Test URL construction with different driver IDs"""
        test_cases = [
            {
                "template": "driver_results",
                "params": {"season": "2023", "driver": "max verstappen"},
                "expected": "http://ergast.com/api/f1/2023/drivers/max_verstappen/results.json"
            },
            {
                "template": "driver_qualifying",
                "params": {"season": "2023", "driver": "lewis hamilton"},
                "expected": "http://ergast.com/api/f1/2023/drivers/hamilton/qualifying.json"
            }
        ]
        
        for case in test_cases:
            url = build_url(case["template"], **case["params"])
            self.assertEqual(url, case["expected"])

if __name__ == '__main__':
    unittest.main() 