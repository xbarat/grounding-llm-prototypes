"""Test fixtures and configuration for pytest"""

import pytest
import httpx
import asyncio
from typing import AsyncGenerator, Dict, Optional, Generator

from backend.tests.f1_test_data import (
    generate_race_calendar,
    generate_driver_standings,
    generate_race_results,
    generate_qualifying_results
)
from backend.tests.test_config import API_CONFIG, TEST_DATA

class MockResponse:
    def __init__(self, status_code: int, json_data: Dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> Dict:
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPError(f"HTTP Error: {self.status_code}")

class MockF1Client:
    def __init__(self):
        self.test_data = {
            "races": generate_race_calendar(
                year=TEST_DATA["year"],
                num_races=TEST_DATA["num_races"]
            ),
            "driver_standings": generate_driver_standings(
                num_drivers=TEST_DATA["num_drivers"]
            ),
            "race_results": generate_race_results(
                num_drivers=TEST_DATA["num_drivers"]
            ),
            "qualifying_results": generate_qualifying_results(
                num_drivers=TEST_DATA["num_drivers"]
            )
        }

    async def get_current_season_schedule(self) -> MockResponse:
        return MockResponse(200, {
            "MRData": {
                "RaceTable": {
                    "Races": self.test_data["races"]
                }
            }
        })

    async def get_driver_standings(self, season: Optional[str] = None) -> MockResponse:
        return MockResponse(200, {
            "MRData": {
                "StandingsTable": {
                    "StandingsLists": [{
                        "DriverStandings": self.test_data["driver_standings"]
                    }]
                }
            }
        })

    async def get_constructor_standings(self, season: Optional[str] = None) -> MockResponse:
        constructors = []
        for i in range(1, 11):  # 10 teams
            constructors.append({
                "position": str(i),
                "positionText": str(i),
                "points": str(400 - (i - 1) * 40),
                "wins": str(max(0, 8 - i)),
                "Constructor": {
                    "constructorId": f"constructor_{i}",
                    "name": f"Test Constructor {i}",
                    "nationality": "Test Nationality"
                }
            })
        
        return MockResponse(200, {
            "MRData": {
                "StandingsTable": {
                    "StandingsLists": [{
                        "ConstructorStandings": constructors
                    }]
                }
            }
        })

    async def get_race_results(self, season: Optional[str] = None, round: Optional[str] = None) -> MockResponse:
        return MockResponse(200, {
            "MRData": {
                "RaceTable": {
                    "Races": [{
                        "Results": self.test_data["race_results"]
                    }]
                }
            }
        })

    async def get_qualifying_results(self, season: Optional[str] = None, round: Optional[str] = None) -> MockResponse:
        return MockResponse(200, {
            "MRData": {
                "RaceTable": {
                    "Races": [{
                        "QualifyingResults": self.test_data["qualifying_results"]
                    }]
                }
            }
        })

@pytest.fixture
async def mock_f1_client() -> AsyncGenerator[MockF1Client, None]:
    """Fixture that provides a mock F1 API client for testing."""
    client = MockF1Client()
    yield client

@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()