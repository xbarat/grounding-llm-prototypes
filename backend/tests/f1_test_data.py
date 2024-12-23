"""Test data generator for F1 API integration tests"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

def generate_race_calendar(year: int = 2024, num_races: int = 23) -> List[Dict[str, Any]]:
    """Generate a realistic F1 race calendar"""
    races = []
    start_date = datetime(year, 3, 1)  # Season typically starts in March
    
    circuits = [
        ("Bahrain", "Sakhir", "BHR"),
        ("Saudi Arabia", "Jeddah", "SAU"),
        ("Australia", "Melbourne", "AUS"),
        ("Japan", "Suzuka", "JPN"),
        ("China", "Shanghai", "CHN"),
        ("Miami", "Miami", "USA"),
        ("Italy", "Imola", "ITA"),
        ("Monaco", "Monte Carlo", "MCO"),
        ("Spain", "Barcelona", "ESP"),
        ("Canada", "Montreal", "CAN"),
        ("Austria", "Spielberg", "AUT"),
        ("Great Britain", "Silverstone", "GBR"),
        ("Hungary", "Budapest", "HUN"),
        ("Belgium", "Spa", "BEL"),
        ("Netherlands", "Zandvoort", "NLD"),
        ("Italy", "Monza", "ITA"),
        ("Singapore", "Marina Bay", "SGP"),
        ("Japan", "Suzuka", "JPN"),
        ("Qatar", "Lusail", "QAT"),
        ("United States", "Austin", "USA"),
        ("Mexico", "Mexico City", "MEX"),
        ("Brazil", "São Paulo", "BRA"),
        ("Las Vegas", "Las Vegas", "USA"),
        ("Abu Dhabi", "Yas Marina", "ARE")
    ]
    
    for i in range(min(num_races, len(circuits))):
        race_date = start_date + timedelta(days=i*14)  # Races typically 2 weeks apart
        circuit = circuits[i]
        
        races.append({
            "season": str(year),
            "round": str(i + 1),
            "raceName": f"{circuit[0]} Grand Prix",
            "Circuit": {
                "circuitId": circuit[1].lower().replace(" ", "_"),
                "circuitName": f"{circuit[1]} Circuit",
                "Location": {
                    "country": circuit[0],
                    "locality": circuit[1],
                    "lat": "0",
                    "long": "0"
                }
            },
            "date": race_date.strftime("%Y-%m-%d"),
            "time": "13:00:00Z"
        })
    
    return races

def generate_driver_standings(num_drivers: int = 20) -> List[Dict[str, Any]]:
    """Generate realistic driver standings"""
    drivers = [
        ("Max", "Verstappen", "NLD", "red_bull"),
        ("Sergio", "Perez", "MEX", "red_bull"),
        ("Charles", "Leclerc", "MCO", "ferrari"),
        ("Carlos", "Sainz", "ESP", "ferrari"),
        ("Lewis", "Hamilton", "GBR", "mercedes"),
        ("George", "Russell", "GBR", "mercedes"),
        ("Lando", "Norris", "GBR", "mclaren"),
        ("Oscar", "Piastri", "AUS", "mclaren"),
        ("Fernando", "Alonso", "ESP", "aston_martin"),
        ("Lance", "Stroll", "CAN", "aston_martin"),
        ("Pierre", "Gasly", "FRA", "alpine"),
        ("Esteban", "Ocon", "FRA", "alpine"),
        ("Alexander", "Albon", "THA", "williams"),
        ("Logan", "Sargeant", "USA", "williams"),
        ("Valtteri", "Bottas", "FIN", "kick_sauber"),
        ("Zhou", "Guanyu", "CHN", "kick_sauber"),
        ("Yuki", "Tsunoda", "JPN", "rb"),
        ("Daniel", "Ricciardo", "AUS", "rb"),
        ("Kevin", "Magnussen", "DNK", "haas"),
        ("Nico", "Hulkenberg", "DEU", "haas")
    ]
    
    standings = []
    total_points = 400  # Reasonable points for top driver
    
    for i in range(min(num_drivers, len(drivers))):
        driver = drivers[i]
        # Points follow roughly exponential decay
        points = total_points * np.exp(-0.2 * i)
        wins = max(0, int(points / 25))  # Approximate wins based on points
        
        standings.append({
            "position": str(i + 1),
            "points": str(round(points, 1)),
            "wins": str(wins),
            "Driver": {
                "driverId": f"{driver[0].lower()}_{driver[1].lower()}",
                "givenName": driver[0],
                "familyName": driver[1],
                "nationality": driver[2]
            },
            "Constructors": [{
                "constructorId": driver[3],
                "name": driver[3].replace("_", " ").title(),
                "nationality": driver[2]
            }]
        })
    
    return standings

def generate_race_results(num_drivers: int = 20) -> List[Dict[str, Any]]:
    """Generate realistic race results"""
    base_time = "1:30:00.000"
    results = []
    
    for i in range(num_drivers):
        # Add random time gaps between drivers
        gap = timedelta(seconds=np.random.exponential(2) if i > 0 else 0)
        status = "Finished" if np.random.random() > 0.15 else np.random.choice(
            ["Collision", "Technical", "Engine", "Gearbox", "Hydraulics"]
        )
        
        results.append({
            "position": str(i + 1) if status == "Finished" else "DNF",
            "points": str(max(0, [25,18,15,12,10,8,6,4,2,1][i]) if i < 10 and status == "Finished" else 0),
            "grid": str(np.random.randint(1, num_drivers + 1)),
            "laps": "58" if status == "Finished" else str(np.random.randint(1, 58)),
            "status": status,
            "Time": {
                "time": str(gap) if status == "Finished" else None
            } if i > 0 else {
                "time": base_time
            }
        })
    
    return results

def generate_qualifying_results(num_drivers: int = 20) -> List[Dict[str, Any]]:
    """Generate realistic qualifying results"""
    base_time = "1:20.000"
    results = []
    
    for i in range(num_drivers):
        # Q1, Q2, Q3 times with progressive improvement
        q1_gap = np.random.normal(1.5, 0.3)
        q2_gap = np.random.normal(1.0, 0.2) if i < 15 else None
        q3_gap = np.random.normal(0.5, 0.1) if i < 10 else None
        
        results.append({
            "position": str(i + 1),
            "Q1": f"1:{20 + q1_gap:.3f}",
            "Q2": f"1:{20 + q2_gap:.3f}" if q2_gap is not None else None,
            "Q3": f"1:{20 + q3_gap:.3f}" if q3_gap is not None else None
        })
    
    return results

def generate_test_dataframe() -> pd.DataFrame:
    """Generate a DataFrame for testing analysis queries"""
    races = generate_race_calendar()
    results = []
    
    for race in races:
        race_results = generate_race_results()
        for result in race_results:
            results.append({
                'race': race['raceName'],
                'round': int(race['round']),
                'date': race['date'],
                'position': int(result['position']) if result['position'] != 'DNF' else None,
                'points': float(result['points']),
                'grid': int(result['grid']),
                'laps': int(result['laps']),
                'status': result['status']
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Example usage
    print("\nGenerating race calendar...")
    races = generate_race_calendar()
    print(f"Generated {len(races)} races")
    
    print("\nGenerating driver standings...")
    standings = generate_driver_standings()
    print(f"Generated standings for {len(standings)} drivers")
    
    print("\nGenerating race results...")
    results = generate_race_results()
    print(f"Generated results for {len(results)} drivers")
    
    print("\nGenerating qualifying results...")
    qualifying = generate_qualifying_results()
    print(f"Generated qualifying results for {len(qualifying)} drivers")
    
    print("\nGenerating test DataFrame...")
    df = generate_test_dataframe()
    print("\nDataFrame head:")
    print(df.head())
    print("\nDataFrame info:")
    print(df.info()) 