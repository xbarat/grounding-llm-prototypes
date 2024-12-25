"""
F1 API Integration Module

This module provides a unified interface for interacting with the Ergast F1 API.
It includes methods for fetching driver standings, race results, qualifying data,
and other F1-related information.
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class F1API:
    """
    Formula 1 API Client for the Ergast API.
    Provides methods to fetch various F1 statistics and race information.
    """
    
    BASE_URL = "http://ergast.com/api/f1"
    CACHE_DURATION = 3600  # 1 hour in seconds

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GIRAFFE-F1-Integration/0.9',
            'Accept': 'application/json'
        })

    @staticmethod
    def _handle_response(response: requests.Response) -> Dict:
        """Handle API response and potential errors."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"F1 API request failed: {str(e)}")
            raise

    @lru_cache(maxsize=128)
    def fetch_season_schedule(self, season: Optional[int] = None) -> Dict:
        """Fetch the race schedule for a given season."""
        url = f"{self.BASE_URL}/{season or 'current'}.json"
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_driver_standings(self, season: Optional[int] = None) -> Dict:
        """Fetch current or historical driver standings."""
        url = f"{self.BASE_URL}/{season or 'current'}/driverStandings.json"
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_constructor_standings(self, season: Optional[int] = None) -> Dict:
        """Fetch current or historical constructor standings."""
        url = f"{self.BASE_URL}/{season or 'current'}/constructorStandings.json"
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_race_results(self, season: Optional[int] = None, round: Optional[int] = None) -> Dict:
        """Fetch results for a specific race or the last race."""
        url = f"{self.BASE_URL}/{season or 'current'}/{round or 'last'}/results.json"
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_qualifying_results(self, season: Optional[int] = None, round: Optional[int] = None) -> Dict:
        """Fetch qualifying results for a specific race or the last race."""
        url = f"{self.BASE_URL}/{season or 'current'}/{round or 'last'}/qualifying.json"
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_driver_results(self, driver_id: str, season: Optional[int] = None) -> Dict:
        """Fetch results for a specific driver, optionally filtered by season."""
        base_url = f"{self.BASE_URL}/drivers/{driver_id}/results.json"
        url = f"{self.BASE_URL}/{season}/drivers/{driver_id}/results.json" if season else base_url
        response = self.session.get(url)
        return self._handle_response(response)

    @lru_cache(maxsize=128)
    def fetch_circuit_results(self, circuit_id: str, limit: Optional[int] = None) -> Dict:
        """Fetch historical results for a specific circuit."""
        url = f"{self.BASE_URL}/circuits/{circuit_id}/results.json"
        if limit:
            url += f"?limit={limit}"
        response = self.session.get(url)
        return self._handle_response(response)

    def fetch_driver_comparison(self, driver1_id: str, driver2_id: str, season: Optional[int] = None) -> Dict:
        """Fetch and compare results for two drivers."""
        driver1_results = self.fetch_driver_results(driver1_id, season)
        driver2_results = self.fetch_driver_results(driver2_id, season)
        return {
            'driver1': driver1_results,
            'driver2': driver2_results
        }

    def fetch_team_performance(self, constructor_id: str, season: Optional[int] = None) -> Dict:
        """Fetch comprehensive team performance data."""
        url = f"{self.BASE_URL}/constructors/{constructor_id}/results.json"
        if season:
            url = f"{self.BASE_URL}/{season}/constructors/{constructor_id}/results.json"
        response = self.session.get(url)
        return self._handle_response(response)

    def clear_cache(self):
        """Clear the LRU cache for all methods."""
        self.fetch_season_schedule.cache_clear()
        self.fetch_driver_standings.cache_clear()
        self.fetch_constructor_standings.cache_clear()
        self.fetch_race_results.cache_clear()
        self.fetch_qualifying_results.cache_clear()
        self.fetch_driver_results.cache_clear()
        self.fetch_circuit_results.cache_clear()

    def __del__(self):
        """Cleanup method to close the session."""
        self.session.close()

# Example usage:
# f1_api = F1API()
# current_standings = f1_api.fetch_driver_standings()
# last_race = f1_api.fetch_race_results()
# verstappen_results = f1_api.fetch_driver_results('max_verstappen') 