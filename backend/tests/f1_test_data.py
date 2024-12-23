"""Test data generator for F1 API integration tests"""

from typing import Dict, List
from datetime import datetime, timedelta

def generate_race_calendar(year: int = 2024, num_races: int = 23) -> List[Dict]:
    """Generate a test race calendar for the specified year."""
    races = []
    base_date = datetime(year, 3, 1)  # Season typically starts in March
    
    for round_num in range(1, num_races + 1):
        race_date = base_date + timedelta(days=14 * round_num)  # Races typically 2 weeks apart
        race = {
            "season": str(year),
            "round": str(round_num),
            "raceName": f"{['Bahrain', 'Saudi Arabian', 'Australian', 'Japanese', 'Chinese', 'Miami', 'Monaco', 'Spanish', 'Canadian', 'Austrian', 'British', 'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Singapore', 'United States', 'Mexican', 'Brazilian', 'Las Vegas', 'Qatar', 'Abu Dhabi'][round_num % 22]} Grand Prix",
            "Circuit": {
                "circuitId": f"circuit_{round_num}",
                "circuitName": f"Test Circuit {round_num}",
                "Location": {
                    "lat": "0.0",
                    "long": "0.0",
                    "locality": "Test City",
                    "country": "Test Country"
                }
            },
            "date": race_date.strftime("%Y-%m-%d"),
            "time": "13:00:00Z"
        }
        races.append(race)
    
    return races

def generate_driver_standings(num_drivers: int = 20) -> List[Dict]:
    """Generate test driver standings."""
    drivers = []
    points_gap = 25  # Approximate points gap between positions
    
    for pos in range(1, num_drivers + 1):
        driver = {
            "position": str(pos),
            "positionText": str(pos),
            "points": str(400 - (pos - 1) * points_gap),
            "wins": str(max(0, 10 - pos)),
            "Driver": {
                "driverId": f"driver_{pos}",
                "permanentNumber": str(pos + 10),
                "code": f"D{pos:02d}",
                "url": f"http://example.com/driver_{pos}",
                "givenName": f"Test",
                "familyName": f"Driver {pos}",
                "dateOfBirth": "1990-01-01",
                "nationality": "Test Nationality"
            },
            "Constructors": [{
                "constructorId": f"constructor_{(pos-1)//2 + 1}",
                "name": f"Test Constructor {(pos-1)//2 + 1}",
                "nationality": "Test Nationality"
            }]
        }
        drivers.append(driver)
    
    return drivers

def generate_race_results(num_drivers: int = 20) -> List[Dict]:
    """Generate test race results."""
    results = []
    base_time = datetime.strptime("1:30:00.000", "%H:%M:%S.%f")
    
    for pos in range(1, num_drivers + 1):
        # Add some randomness to finishing times
        finish_time = base_time + timedelta(seconds=pos * 1.5)
        
        result = {
            "number": str(pos + 10),
            "position": str(pos),
            "positionText": str(pos),
            "points": str(max(0, [25, 18, 15, 12, 10, 8, 6, 4, 2, 1][pos-1] if pos <= 10 else 0)),
            "Driver": {
                "driverId": f"driver_{pos}",
                "permanentNumber": str(pos + 10),
                "code": f"D{pos:02d}",
                "url": f"http://example.com/driver_{pos}",
                "givenName": f"Test",
                "familyName": f"Driver {pos}",
                "dateOfBirth": "1990-01-01",
                "nationality": "Test Nationality"
            },
            "Constructor": {
                "constructorId": f"constructor_{(pos-1)//2 + 1}",
                "name": f"Test Constructor {(pos-1)//2 + 1}",
                "nationality": "Test Nationality"
            },
            "grid": str(pos),
            "laps": "58",
            "status": "Finished" if pos <= 18 else "DNF",
            "Time": {
                "millis": str(int(finish_time.timestamp() * 1000)),
                "time": finish_time.strftime("%M:%S.%f")[:-3]
            } if pos <= 18 else None
        }
        results.append(result)
    
    return results

def generate_qualifying_results(num_drivers: int = 20) -> List[Dict]:
    """Generate test qualifying results."""
    results = []
    base_time = datetime.strptime("1:20:00.000", "%H:%M:%S.%f")
    
    for pos in range(1, num_drivers + 1):
        # Add some randomness to qualifying times
        q_time = base_time + timedelta(milliseconds=pos * 100)
        
        result = {
            "number": str(pos + 10),
            "position": str(pos),
            "Driver": {
                "driverId": f"driver_{pos}",
                "code": f"D{pos:02d}",
                "url": f"http://example.com/driver_{pos}",
                "givenName": f"Test",
                "familyName": f"Driver {pos}",
                "dateOfBirth": "1990-01-01",
                "nationality": "Test Nationality"
            },
            "Constructor": {
                "constructorId": f"constructor_{(pos-1)//2 + 1}",
                "name": f"Test Constructor {(pos-1)//2 + 1}",
                "nationality": "Test Nationality"
            },
            "Q1": q_time.strftime("%M:%S.%f")[:-3],
            "Q2": q_time.strftime("%M:%S.%f")[:-3] if pos <= 15 else None,
            "Q3": q_time.strftime("%M:%S.%f")[:-3] if pos <= 10 else None
        }
        results.append(result)
    
    return results

def generate_test_dataframe() -> Dict:
    """Generate a complete test dataset."""
    return {
        "races": generate_race_calendar(),
        "driver_standings": generate_driver_standings(),
        "race_results": generate_race_results(),
        "qualifying_results": generate_qualifying_results()
    } 