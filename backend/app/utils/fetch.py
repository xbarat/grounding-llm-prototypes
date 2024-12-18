from typing import Optional, Dict, List, Any
import requests
import json

def fetch_user_stats(username: str) -> Optional[Dict]:
    """Fetch user statistics from TypeRacer API."""
    try:
        url = f'https://data.typeracer.com/users'
        params = {
            'id': f'tr:{username}',
            'universe': 'play'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch user stats: {str(e)}")
        return None

def fetch_data(player_id: str, universe: str, n: int, before_id: str = None) -> Optional[List[Dict[str, Any]]]:
    """Fetch data from TypeRacer API with improved error handling"""
    url = f'https://data.typeracer.com/games'
    params = {
        'playerId': player_id,
        'universe': universe,
        'n': n,
        'beforeId': before_id
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            print("No data returned from API")
            return None
        return data
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON response from API")
        return None

def load_data_from_db():
    pass 