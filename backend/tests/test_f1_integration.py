import pytest
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

BASE_URL = "http://ergast.com/api/f1"

class F1APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def close(self):
        await self.client.aclose()

    async def get_current_season_schedule(self) -> List[Dict]:
        """Fetch the current season's race schedule."""
        url = f"{self.base_url}/current.json"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["MRData"]["RaceTable"]["Races"]

    async def get_driver_standings(self, season: Optional[str] = None) -> List[Dict]:
        """Fetch driver standings for a given season or current season."""
        season_path = season if season else "current"
        url = f"{self.base_url}/{season_path}/driverStandings.json"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

    async def get_constructor_standings(self, season: Optional[str] = None) -> List[Dict]:
        """Fetch constructor standings for a given season or current season."""
        season_path = season if season else "current"
        url = f"{self.base_url}/{season_path}/constructorStandings.json"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]

    async def get_race_results(self, season: Optional[str] = None, round: Optional[str] = None) -> List[Dict]:
        """Fetch race results for a specific race or the last race."""
        season_path = season if season else "current"
        round_path = f"/{round}" if round else "/last"
        url = f"{self.base_url}/{season_path}{round_path}/results.json"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["MRData"]["RaceTable"]["Races"][0]["Results"]

@pytest.fixture
async def f1_client():
    client = F1APIClient()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_get_current_season_schedule(f1_client):
    races = await f1_client.get_current_season_schedule()
    assert len(races) > 0
    first_race = races[0]
    assert "raceName" in first_race
    assert "Circuit" in first_race
    assert "date" in first_race
    assert datetime.strptime(first_race["date"], "%Y-%m-%d")

@pytest.mark.asyncio
async def test_get_driver_standings(f1_client):
    standings = await f1_client.get_driver_standings()
    assert len(standings) > 0
    first_driver = standings[0]
    assert "position" in first_driver
    assert "Driver" in first_driver
    assert "points" in first_driver
    assert float(first_driver["points"]) >= 0

@pytest.mark.asyncio
async def test_get_constructor_standings(f1_client):
    standings = await f1_client.get_constructor_standings()
    assert len(standings) > 0
    first_constructor = standings[0]
    assert "position" in first_constructor
    assert "Constructor" in first_constructor
    assert "points" in first_constructor
    assert float(first_constructor["points"]) >= 0

@pytest.mark.asyncio
async def test_get_race_results(f1_client):
    results = await f1_client.get_race_results()
    assert len(results) > 0
    first_result = results[0]
    assert "position" in first_result
    assert "Driver" in first_result
    assert "Constructor" in first_result
    assert "Time" in first_result or "status" in first_result  # DNF drivers won't have Time

@pytest.mark.asyncio
async def test_error_handling(f1_client):
    with pytest.raises(httpx.HTTPError):
        await f1_client.get_race_results(season="invalid", round="999") 