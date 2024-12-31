import unittest
from data2 import DataPipeline, DataRequirements

class TestEndpointConstruction(unittest.TestCase):
    def setUp(self):
        self.pipeline = DataPipeline()
    
    def test_qualifying_monaco_url(self):
        """Test URL construction for Monaco qualifying query"""
        requirements = DataRequirements(
            endpoint="/api/f1/qualifying",
            params={"season": "2023", "round": "6", "driver": "leclerc"}
        )
        url = self.pipeline._build_url(requirements)
        expected = "http://ergast.com/api/f1/2023/6/qualifying.json"
        self.assertEqual(url, expected)
    
    def test_qualifying_full_season_url(self):
        """Test URL construction for full season qualifying query"""
        requirements = DataRequirements(
            endpoint="/api/f1/qualifying",
            params={"season": "2023", "driver": "piastri"}
        )
        url = self.pipeline._build_url(requirements)
        expected = "http://ergast.com/api/f1/2023/qualifying.json"
        self.assertEqual(url, expected)
    
    def test_circuit_specific_url(self):
        """Test URL construction for circuit-specific query"""
        requirements = DataRequirements(
            endpoint="/api/f1/results",
            params={"season": "2023", "round": "10", "driver": "russell"}
        )
        url = self.pipeline._build_url(requirements)
        expected = "http://ergast.com/api/f1/2023/10/results.json"
        self.assertEqual(url, expected)

if __name__ == '__main__':
    unittest.main() 