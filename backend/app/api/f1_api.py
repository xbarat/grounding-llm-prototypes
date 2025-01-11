"""F1 API handling and response processing"""

from typing import Dict, Any, Optional, List
import requests
import pandas as pd
from datetime import datetime
from ratelimit import limits, sleep_and_retry

ERGAST_BASE_URL = "http://ergast.com/api/f1"
CALLS_PER_SECOND = 4

class F1ResponseProcessor:
    """Process different types of F1 API responses into DataFrames"""
    
    @staticmethod
    def process_drivers(data: Dict[str, Any]) -> pd.DataFrame:
        """Process driver data response"""
        drivers = data['MRData']['DriverTable']['Drivers']
        df = pd.DataFrame(drivers)
        if not df.empty:
            df['full_name'] = df['givenName'] + ' ' + df['familyName']
            df['nationality'] = df['nationality']
            # Convert dateOfBirth to datetime
            df['dateOfBirth'] = pd.to_datetime(df['dateOfBirth'])
        return df
    
    @staticmethod
    def process_race_results(data: Dict[str, Any]) -> pd.DataFrame:
        """Process race results data"""
        races = data['MRData']['RaceTable']['Races']
        results = []
        
        for race in races:
            race_info = {
                'race_name': race['raceName'],
                'circuit': race['Circuit']['circuitName'],
                'date': race['date'],
                'season': race['season'],
                'round': race['round']
            }
            
            for result in race['Results']:
                row = {
                    **race_info,
                    'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                    'constructor': result['Constructor']['name'],
                    'position': int(result['position']),
                    'points': float(result['points']),
                    'status': result['status'],
                    'grid': int(result['grid']),
                    'laps': int(result['laps'])
                }
                
                # Add fastest lap if available
                if 'FastestLap' in result:
                    row.update({
                        'fastest_lap_rank': int(result['FastestLap']['rank']),
                        'fastest_lap_time': result['FastestLap']['Time']['time'],
                        'fastest_lap_speed': float(result['FastestLap']['AverageSpeed']['speed'])
                    })
                
                results.append(row)
        
        return pd.DataFrame(results)
    
    @staticmethod
    def process_qualifying(data: Dict[str, Any]) -> pd.DataFrame:
        """Process qualifying data"""
        races = data['MRData']['RaceTable']['Races']
        results = []
        
        for race in races:
            for quali in race['QualifyingResults']:
                results.append({
                    'race_name': race['raceName'],
                    'circuit': race['Circuit']['circuitName'],
                    'date': race['date'],
                    'driver': f"{quali['Driver']['givenName']} {quali['Driver']['familyName']}",
                    'constructor': quali['Constructor']['name'],
                    'position': int(quali['position']),
                    'Q1': quali.get('Q1', None),
                    'Q2': quali.get('Q2', None),
                    'Q3': quali.get('Q3', None)
                })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def process_standings(data: Dict[str, Any], standings_type: str = 'driver') -> pd.DataFrame:
        """Process standings data"""
        standings_list = data['MRData']['StandingsTable']['StandingsLists']
        results = []
        
        for standing in standings_list:
            standings_key = 'DriverStandings' if standings_type == 'driver' else 'ConstructorStandings'
            
            for pos in standing[standings_key]:
                result = {
                    'position': int(pos['position']),
                    'points': float(pos['points']),
                    'wins': int(pos['wins']),
                    'season': standing['season'],
                    'round': standing['round']
                }
                
                if standings_type == 'driver':
                    result['name'] = f"{pos['Driver']['givenName']} {pos['Driver']['familyName']}"
                    result['constructor'] = pos['Constructors'][0]['name']
                else:
                    result['name'] = pos['Constructor']['name']
                    result['nationality'] = pos['Constructor']['nationality']
                
                results.append(result)
        
        return pd.DataFrame(results)

@sleep_and_retry
@limits(calls=CALLS_PER_SECOND, period=1)
async def fetch_f1_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch data from F1 API with automatic response processing"""
    try:
        url = f"{ERGAST_BASE_URL}{endpoint}.json"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Determine response type and process accordingly
        data = response.json()
        processor = F1ResponseProcessor()
        
        if 'drivers' in endpoint:
            df = processor.process_drivers(data)
        elif 'results' in endpoint:
            df = processor.process_race_results(data)
        elif 'qualifying' in endpoint:
            df = processor.process_qualifying(data)
        elif 'standings' in endpoint:
            standings_type = 'driver' if 'driver' in endpoint else 'constructor'
            df = processor.process_standings(data, standings_type)
        else:
            df = pd.DataFrame(data['MRData'])
        
        return {
            'success': True,
            'data': df,
            'metadata': {
                'url': url,
                'params': params,
                'timestamp': datetime.now().isoformat(),
                'rows': len(df)
            }
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'metadata': {
                'url': url if 'url' in locals() else None,
                'params': params,
                'timestamp': datetime.now().isoformat()
            }
        }

def build_endpoint(endpoint_type: str, **kwargs) -> str:
    """Build endpoint URL with parameters"""
    from .f1_endpoints import F1Endpoints
    category, subtype = endpoint_type.split('.')
    endpoint_template = getattr(F1Endpoints, category)[subtype]
    return endpoint_template.format(**kwargs) 