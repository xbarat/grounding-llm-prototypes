"""Integration tests for F1 API"""

import pytest
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from .conftest import MockResponse

@pytest.mark.asyncio
async def test_get_current_season_schedule(mock_f1_client):
    """Test fetching current season race schedule."""
    response = await mock_f1_client.get_current_season_schedule()
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    
    assert len(races) > 0
    first_race = races[0]
    assert "raceName" in first_race
    assert "Circuit" in first_race
    assert "date" in first_race
    assert datetime.strptime(first_race["date"], "%Y-%m-%d")

@pytest.mark.asyncio
async def test_get_driver_standings(mock_f1_client):
    """Test fetching driver standings."""
    response = await mock_f1_client.get_driver_standings()
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
    
    assert len(standings) > 0
    first_driver = standings[0]
    assert "position" in first_driver
    assert "Driver" in first_driver
    assert "points" in first_driver
    assert float(first_driver["points"]) >= 0

@pytest.mark.asyncio
async def test_get_constructor_standings(mock_f1_client):
    """Test fetching constructor standings."""
    response = await mock_f1_client.get_constructor_standings()
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
    
    assert len(standings) > 0
    first_constructor = standings[0]
    assert "position" in first_constructor
    assert "Constructor" in first_constructor
    assert "points" in first_constructor
    assert float(first_constructor["points"]) >= 0

@pytest.mark.asyncio
async def test_get_race_results(mock_f1_client):
    """Test fetching race results."""
    response = await mock_f1_client.get_race_results()
    data = response.json()
    results = data["MRData"]["RaceTable"]["Races"][0]["Results"]
    
    assert len(results) > 0
    first_result = results[0]
    assert "position" in first_result
    assert "Driver" in first_result
    assert "Constructor" in first_result
    assert "Time" in first_result or "status" in first_result  # DNF drivers won't have Time

@pytest.mark.asyncio
async def test_get_qualifying_results(mock_f1_client):
    """Test fetching qualifying results."""
    response = await mock_f1_client.get_qualifying_results()
    data = response.json()
    results = data["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"]
    
    assert len(results) > 0
    first_result = results[0]
    assert "position" in first_result
    assert "Driver" in first_result
    assert "Constructor" in first_result
    assert "Q1" in first_result  # All drivers must have Q1 time
    # Q2 and Q3 are optional as not all drivers progress

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling for invalid requests."""
    with pytest.raises(httpx.HTTPError):
        response = MockResponse(404, {})
        response.raise_for_status()