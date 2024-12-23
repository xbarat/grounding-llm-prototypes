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

        # 6. Specific Driver Season Results
        print("\n=== Max Verstappen's 2023 Results ===")
        driver_results = await fetch_data("2023/drivers/max_verstappen/results")
        driver_races = driver_results["MRData"]["RaceTable"]["Races"]
        print(f"Number of races: {len(driver_races)}")
        print("Last race result:")
        print(json.dumps(driver_races[-1], indent=2))

        # 7. Specific Circuit History
        print("\n=== Monaco GP Last 5 Winners ===")
        circuit_results = await fetch_data("circuits/monaco/results/1")
        circuit_races = circuit_results["MRData"]["RaceTable"]["Races"]
        print(f"Most recent winner:")
        print(json.dumps(circuit_races[0]["Results"][0], indent=2))

        # 8. Head to Head - Last Race
        print("\n=== Verstappen vs Hamilton Last Race ===")
        last_race = await fetch_data("current/last/results")
        race_data = last_race["MRData"]["RaceTable"]["Races"][0]
        results = race_data["Results"]
        ver_result = next((r for r in results if r["Driver"]["code"] == "VER"), None)
        ham_result = next((r for r in results if r["Driver"]["code"] == "HAM"), None)
        print(f"Race: {race_data['raceName']}")
        if ver_result and ham_result:
            print(f"Verstappen: P{ver_result['position']} - Hamilton: P{ham_result['position']}")
            print("Details:")
            print(json.dumps({
                "VER": {"position": ver_result["position"], "points": ver_result["points"]},
                "HAM": {"position": ham_result["position"], "points": ham_result["points"]}
            }, indent=2))

    except httpx.HTTPError as e:
        print(f"HTTP Error: {e}")
    except KeyError as e:
        print(f"Data structure error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_endpoints()) 