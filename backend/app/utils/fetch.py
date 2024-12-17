from typing import Optional, Dict
import requests

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

def fetch_data(player_id: str, universe: str, n: int):
    pass

def load_data_from_db():
    pass 