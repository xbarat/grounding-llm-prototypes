"""Test script to explore Ergast F1 API endpoints"""

import httpx
import asyncio
from typing import Dict, Any
import json
from datetime import datetime

BASE_URL = "http://ergast.com/api/f1"

async def fetch_data(endpoint: str) -> Dict[str, Any]:
    """Fetch data from the Ergast API."""
    url = f"{BASE_URL}/{endpoint}.json"
    print(f"\nFetching from: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def explore_endpoints():
    """Explore various Ergast API endpoints."""
    try:
        # 1. Current Season Schedule
        print("\n=== Current Season Schedule ===")
        schedule = await fetch_data("current")
        races = schedule["MRData"]["RaceTable"]["Races"]
        print(f"Number of races: {len(races)}")
        print("First race:")
        print(json.dumps(races[0], indent=2))

        # 2. Current Driver Standings
        print("\n=== Current Driver Standings ===")
        standings = await fetch_data("current/driverStandings")
        drivers = standings["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        print(f"Number of drivers: {len(drivers)}")
        print("Top driver:")
        print(json.dumps(drivers[0], indent=2))

        # 3. Last Race Results
        print("\n=== Last Race Results ===")
        results = await fetch_data("current/last/results")
        race_results = results["MRData"]["RaceTable"]["Races"][0]["Results"]
        print(f"Number of finishers: {len(race_results)}")
        print("Winner:")
        print(json.dumps(race_results[0], indent=2))

        # 4. Constructor Standings
        print("\n=== Constructor Standings ===")
        constructors = await fetch_data("current/constructorStandings")
        teams = constructors["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
        print(f"Number of teams: {len(teams)}")
        print("Top team:")
        print(json.dumps(teams[0], indent=2))

        # 5. Qualifying Results from Last Race
        print("\n=== Last Race Qualifying ===")
        qualifying = await fetch_data("current/last/qualifying")
        quali_results = qualifying["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]
        print(f"Number of qualifiers: {len(quali_results)}")
        print("Pole position:")
        print(json.dumps(quali_results[0], indent=2))

    except httpx.HTTPError as e:
        print(f"HTTP Error: {e}")
    except KeyError as e:
        print(f"Data structure error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_endpoints()) 