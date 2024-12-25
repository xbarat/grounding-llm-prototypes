"""
Platform data fetcher module.

This module provides functions to fetch data from various platforms like TypeRacer and F1.
"""

from typing import Dict, Any, Optional
import httpx
import logging
from .f1_api import F1API

logger = logging.getLogger(__name__)

async def fetch_typeracer_data(username: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch data from TypeRacer API."""
    base_url = "https://data.typeracer.com/pit/race_history"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}?user={username}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"TypeRacer API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in TypeRacer API request: {str(e)}")
            raise

async def fetch_f1_data(driver_id: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch data from F1 API."""
    async with F1API() as f1_api:
        try:
            if endpoint == "driver_standings":
                return await f1_api.fetch_driver_standings()
            elif endpoint == "race_results":
                return await f1_api.fetch_race_results()
            elif endpoint == "qualifying_results":
                return await f1_api.fetch_qualifying_results()
            elif endpoint == "driver_results":
                return await f1_api.fetch_driver_results(driver_id)
            elif endpoint == "constructor_standings":
                return await f1_api.fetch_constructor_standings()
            else:
                raise ValueError(f"Unknown F1 endpoint: {endpoint}")
        except Exception as e:
            logger.error(f"F1 API request failed: {str(e)}")
            raise

async def fetch_platform_data(platform: str, identifier: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the specified platform.
    
    Args:
        platform: The platform to fetch data from (typeracer or f1)
        identifier: The user/driver identifier
        endpoint: The API endpoint to call
        params: Optional parameters for the API call
    
    Returns:
        Dict containing the platform data
    """
    if platform == "typeracer":
        return await fetch_typeracer_data(identifier, endpoint, params)
    elif platform == "f1":
        return await fetch_f1_data(identifier, endpoint, params)
    else:
        raise ValueError(f"Unsupported platform: {platform}") 