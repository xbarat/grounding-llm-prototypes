from typing import Dict, Any, Optional
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .platform_config import get_platform_config, PlatformConfig, EndpointConfig

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
            "typeracer": None  # TypeRacer doesn't need API key
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
    
    def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
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

    def get_default_queries(self) -> list[str]:
        """Get default analysis queries for the platform"""
        return self.config.default_queries

# Example usage for cricket data
def fetch_cricket_matches(date: Optional[str] = None) -> Dict[str, Any]:
    """Fetch cricket matches data"""
    fetcher = PlatformFetcher("cricinfo")
    params = {"date": date} if date else {}
    return fetcher.fetch_data("matches", params)

def fetch_cricket_player_stats(player_id: str) -> Dict[str, Any]:
    """Fetch cricket player statistics"""
    fetcher = PlatformFetcher("cricinfo")
    return fetcher.fetch_data("players", {"id": player_id})

# Example usage for TypeRacer data (existing functionality)
def fetch_typeracer_stats(user_id: str) -> Dict[str, Any]:
    """Fetch TypeRacer user statistics"""
    fetcher = PlatformFetcher("typeracer")
    return fetcher.fetch_data("user_stats", {"playerId": user_id}) 