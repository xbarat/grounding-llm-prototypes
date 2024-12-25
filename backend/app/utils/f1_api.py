"""
F1 API Integration Module

This module provides a unified interface for interacting with the Ergast F1 API.
It includes methods for fetching driver standings, race results, qualifying data,
and other F1-related information.
"""

from typing import Dict, List, Optional, Any
import httpx
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
        self.client = httpx.AsyncClient(
            headers={
                'User-Agent': 'GIRAFFE-F1-Integration/0.9',
                'Accept': 'application/json'
            },
            timeout=30.0
        )

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an async request to the F1 API."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"F1 API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in F1 API request: {str(e)}")
            raise

    async def fetch_season_schedule(self, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch the race schedule for a given season."""
        endpoint = f"{season or 'current'}.json"
        return await self._make_request(endpoint)

    async def fetch_driver_standings(self, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch current driver standings."""
        endpoint = f"{season or 'current'}/driverStandings.json"
        return await self._make_request(endpoint)

    async def fetch_constructor_standings(self, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch current constructor standings."""
        endpoint = f"{season or 'current'}/constructorStandings.json"
        return await self._make_request(endpoint)

    async def fetch_race_results(self, season: Optional[int] = None, round: Optional[int] = None) -> Dict[str, Any]:
        """Fetch race results."""
        base = f"{season or 'current'}"
        endpoint = f"{base}/{round}/results.json" if round else f"{base}/last/results.json"
        return await self._make_request(endpoint)

    async def fetch_qualifying_results(self, season: Optional[int] = None, round: Optional[int] = None) -> Dict[str, Any]:
        """Fetch qualifying results."""
        base = f"{season or 'current'}"
        endpoint = f"{base}/{round}/qualifying.json" if round else f"{base}/last/qualifying.json"
        return await self._make_request(endpoint)

    async def fetch_driver_results(self, driver_id: str, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch results for a specific driver."""
        endpoint = f"{season or 'current'}/drivers/{driver_id}/results.json"
        return await self._make_request(endpoint)

    async def fetch_circuit_results(self, circuit_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch historical results for a specific circuit."""
        params = {"limit": str(limit)} if limit else None
        endpoint = f"circuits/{circuit_id}/results.json"
        return await self._make_request(endpoint, params)

    async def fetch_driver_comparison(self, driver1_id: str, driver2_id: str, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch and compare results for two drivers."""
        driver1_results = await self.fetch_driver_results(driver1_id, season)
        driver2_results = await self.fetch_driver_results(driver2_id, season)
        return {
            'driver1': driver1_results,
            'driver2': driver2_results
        }

    async def fetch_team_performance(self, constructor_id: str, season: Optional[int] = None) -> Dict[str, Any]:
        """Fetch comprehensive team performance data."""
        endpoint = f"{season or 'current'}/constructors/{constructor_id}/results.json"
        return await self._make_request(endpoint)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    def __del__(self):
        """Cleanup method."""
        import asyncio
        try:
            asyncio.create_task(self.client.aclose())
        except Exception:
            pass

# Example usage:
# f1_api = F1API()
# current_standings = f1_api.fetch_driver_standings()
# last_race = f1_api.fetch_race_results()
# verstappen_results = f1_api.fetch_driver_results('max_verstappen') 