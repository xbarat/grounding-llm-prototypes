from typing import Optional, Dict, List, Any
import requests
import json
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    url = 'https://data.typeracer.com/games'
    params = {
        'playerId': player_id,
        'universe': universe,
        'n': str(n)
    }
    if before_id:
        params['beforeGameId'] = before_id

    try:
        print(f"Fetching data from TypeRacer API: {url} with params: {params}")
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        response.raise_for_status()
        
        data = response.json()
        if not isinstance(data, list):
            print(f"Unexpected response format: {data}")
            return None
        if not data:
            print("No data returned from API")
            return None
        return data
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response from API: {str(e)}")
        return None

def load_data_from_db() -> Optional[pd.DataFrame]:
    """Load data from PostgreSQL database"""
    try:
        # Get database URL from environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("Error: DATABASE_URL not found in environment variables")
            return None

        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Load data into DataFrame
        query = "SELECT * FROM typing_stats"
        df = pd.read_sql_query(query, engine)
        
        if df.empty:
            print("No data found in database")
            return None
            
        return df
    except Exception as e:
        print(f"Error loading database: {str(e)}")
        return None 