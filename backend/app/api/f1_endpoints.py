"""F1 API endpoint configurations and fetching logic"""

from typing import Dict, Any, Optional
import requests
import pandas as pd
from ratelimit import limits, sleep_and_retry

ERGAST_BASE_URL = "http://ergast.com/api/f1"
CALLS_PER_SECOND = 4

class F1Endpoints:
    """F1 API endpoint configurations"""
    
    DRIVERS = {
        'all': '/drivers',
        'year': '/{year}/drivers',
        'race': '/{year}/{round}/drivers',
        'specific': '/drivers/{driverid}'
    }
    
    CONSTRUCTORS = {
        'all': '/constructors',
        'year': '/{year}/constructors',
        'race': '/{year}/{round}/constructors',
        'specific': '/constructors/{constructorid}'
    }
    
    RESULTS = {
        'race': '/{year}/{round}/results',
        'latest': '/current/last/results'
    }
    
    QUALIFYING = {
        'race': '/{year}/{round}/qualifying'
    }
    
    STANDINGS = {
        'driver_race': '/{year}/{round}/driverStandings',
        'driver_season': '/{year}/driverStandings',
        'driver_current': '/current/driverStandings',
        'driver_winners': '/driverStandings/1',
        'driver_specific': '/drivers/{driverid}/driverStandings',
        'constructor_race': '/{year}/{round}/constructorStandings',
        'constructor_season': '/{year}/constructorStandings',
        'constructor_current': '/current/constructorStandings',
        'constructor_winners': '/constructorStandings/1',
        'constructor_specific': '/constructors/{constructorid}/constructorStandings'
    }
    
    SCHEDULES = {
        'year': '/{year}',
        'current': '/current',
        'race': '/{year}/{round}'
    }
    
    LAP_TIMES = {
        'specific': '/{year}/{round}/laps/{lapnumber}'
    }
    
    PIT_STOPS = {
        'race': '/{year}/{round}/pitstops',
        'specific': '/{year}/{round}/pitstops/{pitstopnumber}'
    }

@sleep_and_retry
@limits(calls=CALLS_PER_SECOND, period=1)
async def fetch_f1_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from F1 API with rate limiting
    
    Args:
        endpoint: API endpoint path (e.g., "/drivers")
        params: Optional query parameters
        
    Returns:
        Dictionary containing the API response or error information
    """
    try:
        url = f"{ERGAST_BASE_URL}{endpoint}.json"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return {
            'success': True,
            'data': response.json(),
            'metadata': {
                'url': url,
                'params': params
            }
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'metadata': {
                'url': url if 'url' in locals() else None,
                'params': params
            }
        }

def build_endpoint(endpoint_type: str, **kwargs) -> str:
    """
    Build endpoint URL with parameters
    
    Example:
        build_endpoint('DRIVERS.year', year=2023)
        build_endpoint('STANDINGS.driver_specific', driverid='max_verstappen')
    """
    category, subtype = endpoint_type.split('.')
    endpoint_template = getattr(F1Endpoints, category)[subtype]
    return endpoint_template.format(**kwargs)