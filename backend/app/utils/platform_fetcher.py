from typing import Dict, Any, Optional, List
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .platform_config import get_platform_config, PlatformConfig, EndpointConfig
import pandas as pd

load_dotenv()

class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class DataFetchError(Exception):
    """Raised when data fetch fails"""
    pass

class PlatformFetcher:
    def __init__(self, platform_id: str):
        self.config = get_platform_config(platform_id)
        if not self.config:
            raise ValueError(f"Unknown platform: {platform_id}")
        
        self.api_keys = {
            "cricinfo": os.getenv("CRICAPI_KEY", ""),
            "typeracer": None,  # TypeRacer doesn't need API key
            "f1": None  # Ergast API doesn't need API key
        }
        
        # Rate limiting tracking
        self.request_counts: Dict[str, int] = {}
        self.last_reset: Dict[str, datetime] = {}
    
    def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if we're within rate limits"""
        endpoint_config = self.config.endpoints.get(endpoint)
        if not endpoint_config or not endpoint_config.rate_limit:
            return True
        
        now = datetime.now()
        if endpoint not in self.last_reset or \
           now - self.last_reset[endpoint] > timedelta(minutes=1):
            self.request_counts[endpoint] = 0
            self.last_reset[endpoint] = now
        
        return self.request_counts[endpoint] < endpoint_config.rate_limit
    
    def _increment_rate_limit(self, endpoint: str):
        """Increment the request counter for rate limiting"""
        if endpoint in self.request_counts:
            self.request_counts[endpoint] += 1

    async def fetch_f1_data(self, query_type: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """Fetch and process F1 data based on query type"""
        data = await self.fetch_data(query_type, params)
        if not data:
            return pd.DataFrame()

        if query_type == "driver_standings":
            standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
            return pd.DataFrame([{
                "position": int(d["position"]),
                "points": float(d["points"]),
                "wins": int(d["wins"]),
                "driver_id": d["Driver"]["driverId"],
                "driver_name": f"{d['Driver']['givenName']} {d['Driver']['familyName']}",
                "constructor": d["Constructors"][0]["name"]
            } for d in standings])

        elif query_type == "race_results":
            races = data["MRData"]["RaceTable"]["Races"]
            results = []
            for race in races:
                for result in race["Results"]:
                    results.append({
                        "race": race["raceName"],
                        "round": int(race["round"]),
                        "driver_id": result["Driver"]["driverId"],
                        "driver_name": f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        "constructor": result["Constructor"]["name"],
                        "grid": int(result["grid"]),
                        "position": int(result["position"]),
                        "points": float(result["points"]),
                        "status": result["status"],
                        "fastest_lap": result.get("FastestLap", {}).get("Time", {}).get("time", None)
                    })
            return pd.DataFrame(results)

        elif query_type == "qualifying_results":
            races = data["MRData"]["RaceTable"]["Races"]
            results = []
            for race in races:
                for result in race["QualifyingResults"]:
                    results.append({
                        "race": race["raceName"],
                        "round": int(race["round"]),
                        "driver_id": result["Driver"]["driverId"],
                        "driver_name": f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        "constructor": result["Constructor"]["name"],
                        "position": int(result["position"]),
                        "q1": result.get("Q1", None),
                        "q2": result.get("Q2", None),
                        "q3": result.get("Q3", None)
                    })
            return pd.DataFrame(results)

        return pd.DataFrame()

    async def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data from the specified endpoint"""
        endpoint_config = self.config.endpoints.get(endpoint)
        if not endpoint_config:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        if not self._check_rate_limit(endpoint):
            raise RateLimitError(f"Rate limit exceeded for {endpoint}")
        
        # Prepare request parameters
        request_params = endpoint_config.params.copy()
        if params:
            request_params.update(params)
        
        # Add API key if required
        if endpoint_config.requires_auth:
            api_key = self.api_keys.get(self.config.id)
            if not api_key:
                raise AuthenticationError(f"API key required for {self.config.id}")
            request_params["apikey"] = api_key
        
        # Make the request
        url = f"{self.config.base_url}{endpoint_config.path}"
        try:
            response = requests.request(
                method=endpoint_config.method,
                url=url,
                params=request_params
            )
            response.raise_for_status()
            self._increment_rate_limit(endpoint)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DataFetchError(f"Failed to fetch data: {str(e)}")

    def get_default_queries(self) -> List[str]:
        """Get default analysis queries for the platform"""
        return self.config.default_queries

# Example usage for F1 data
async def fetch_f1_driver_comparison(driver1_id: str, driver2_id: str, year: str = "current") -> pd.DataFrame:
    """Fetch and compare two drivers' performance"""
    fetcher = PlatformFetcher("f1")
    params = {"year": year}
    
    # Fetch race results for both drivers
    results = await fetcher.fetch_f1_data("race_results", params)
    
    # Filter for the specified drivers
    comparison = results[results["driver_id"].isin([driver1_id, driver2_id])]
    return comparison

async def fetch_f1_qualifying_analysis(constructor_id: str, year: str = "current") -> pd.DataFrame:
    """Analyze qualifying performance for a constructor"""
    fetcher = PlatformFetcher("f1")
    params = {"year": year, "constructor": constructor_id}
    
    return await fetcher.fetch_f1_data("qualifying_results", params) 