import pytest
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from app.utils.platform_fetcher import PlatformFetcher
from app.utils.code_utils import generate_code, execute_code_safely
from .f1_test_config import (
    API_CONFIG,
    TEST_DATA,
    REQUIRED_FIELDS,
    TEST_QUERIES,
    VISUALIZATION_TYPES,
    ERROR_MESSAGES,
    CACHE_CONFIG
)

class F1Cache:
    """Simple cache implementation for F1 API responses"""
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.timestamps: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if it exists and hasn't expired"""
        if key in self.cache:
            if time.time() - self.timestamps[key] < CACHE_CONFIG["ttl"]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any]):
        """Cache data with timestamp"""
        if len(self.cache) >= CACHE_CONFIG["max_size"]:
            # Remove oldest entry
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()

class TestF1Integration:
    """Integration tests for Formula 1 data using Ergast API"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.cache = F1Cache() if CACHE_CONFIG["enabled"] else None
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed the API rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < (1.0 / API_CONFIG["rate_limit"]):
            time.sleep((1.0 / API_CONFIG["rate_limit"]) - time_since_last_request)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the F1 API with caching and rate limiting"""
        # Check cache first
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Respect rate limit
        self._respect_rate_limit()
        
        # Make request with retries
        for attempt in range(API_CONFIG["retries"]):
            try:
                url = f"{API_CONFIG['base_url']}/{endpoint}.json"
                response = requests.get(url, params=params, timeout=API_CONFIG["timeout"])
                response.raise_for_status()
                data = response.json()
                
                # Cache successful response
                if self.cache:
                    self.cache.set(cache_key, data)
                
                return data
            except requests.RequestException as e:
                if attempt == API_CONFIG["retries"] - 1:
                    pytest.fail(ERROR_MESSAGES["api_error"].format(error=str(e)))
                time.sleep(1)  # Wait before retry
        
        raise Exception("Should not reach here")
    
    def _validate_fields(self, data: Dict[str, Any], required_fields: List[str], context: str):
        """Validate that all required fields are present"""
        missing_fields = [field for field in required_fields if field not in data]
        assert not missing_fields, ERROR_MESSAGES["missing_data"].format(
            field=f"Missing fields in {context}: {', '.join(missing_fields)}"
        )
    
    @pytest.mark.integration
    def test_current_season_schedule(self):
        """Test fetching current season race schedule"""
        data = self._make_request("current")
        
        # Validate response structure
        assert "MRData" in data
        assert "RaceTable" in data["MRData"]
        assert "Races" in data["MRData"]["RaceTable"]
        
        races = data["MRData"]["RaceTable"]["Races"]
        assert len(races) > 0
        
        # Validate race data structure
        first_race = races[0]
        self._validate_fields(first_race, REQUIRED_FIELDS["race"], "race")
    
    @pytest.mark.integration
    def test_driver_standings(self):
        """Test fetching current driver standings"""
        data = self._make_request("current/driverStandings")
        
        assert "MRData" in data
        assert "StandingsTable" in data["MRData"]
        assert "StandingsLists" in data["MRData"]["StandingsTable"]
        
        standings = data["MRData"]["StandingsTable"]["StandingsLists"]
        if standings:  # If season has started
            drivers = standings[0]["DriverStandings"]
            assert len(drivers) > 0
            
            # Validate driver data structure
            first_driver = drivers[0]
            self._validate_fields(first_driver, REQUIRED_FIELDS["standings"], "driver standings")
            self._validate_fields(first_driver["Driver"], REQUIRED_FIELDS["driver"], "driver")
    
    @pytest.mark.integration
    def test_visualization_integration(self):
        """Test generating visualizations from F1 data"""
        data = self._make_request("current/driverStandings")
        
        if data["MRData"]["StandingsTable"]["StandingsLists"]:
            standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            df = pd.DataFrame([{
                'position': int(d['position']),
                'points': float(d['points']),
                'driver': f"{d['Driver']['givenName']} {d['Driver']['familyName']}",
                'constructor': d['Constructors'][0]['name']
            } for d in standings])
            
            # Test each visualization type
            for viz_type in VISUALIZATION_TYPES:
                plt.figure(figsize=(12, 6))
                
                if viz_type == "line_chart":
                    sns.lineplot(data=df, x='position', y='points')
                elif viz_type == "bar_chart":
                    sns.barplot(data=df.head(10), x='driver', y='points')
                elif viz_type == "scatter_plot":
                    sns.scatterplot(data=df, x='position', y='points')
                elif viz_type == "box_plot":
                    sns.boxplot(data=df, x='constructor', y='points')
                elif viz_type == "heat_map":
                    pivot_data = df.pivot_table(
                        index='constructor',
                        columns='position',
                        values='points',
                        aggfunc='sum'
                    )
                    sns.heatmap(pivot_data, annot=True, cmap='YlOrRd')
                
                plt.title(f'F1 Driver Standings - {viz_type}')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.close()
    
    @pytest.mark.integration
    def test_analysis_queries(self):
        """Test running analysis queries"""
        # Fetch race results for analysis
        races_data = []
        for round_num in range(1, TEST_DATA["rounds_to_test"] + 1):
            try:
                data = self._make_request(f"current/{round_num}/results")
                if data["MRData"]["RaceTable"]["Races"]:
                    races_data.extend(data["MRData"]["RaceTable"]["Races"])
            except:
                continue
        
        if races_data:
            # Prepare DataFrame
            results = []
            for race in races_data:
                for result in race["Results"]:
                    results.append({
                        'race': race['raceName'],
                        'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        'constructor': result['Constructor']['name'],
                        'position': int(result['position']),
                        'points': float(result['points']),
                        'grid': int(result['grid'])
                    })
            
            df = pd.DataFrame(results)
            
            # Test each analysis query
            for query in TEST_QUERIES:
                code_response = generate_code(df, query)
                success, result, _ = execute_code_safely(code_response, df)
                
                assert success, ERROR_MESSAGES["analysis_error"].format(
                    error=f"Failed to execute query: {query}"
                )
                assert result is not None, ERROR_MESSAGES["analysis_error"].format(
                    error=f"No results for query: {query}"
                )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"]) 