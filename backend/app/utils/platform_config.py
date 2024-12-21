from typing import Dict, List, Optional, TypedDict, Literal
from pydantic import BaseModel

class EndpointConfig(BaseModel):
    """Configuration for a specific API endpoint"""
    path: str
    method: Literal["GET", "POST"] = "GET"
    requires_auth: bool = False
    rate_limit: Optional[int] = None  # requests per minute
    params: Dict[str, str] = {}

class PlatformConfig(BaseModel):
    """Configuration for a data platform"""
    id: str
    name: str
    base_url: str
    description: str
    endpoints: Dict[str, EndpointConfig]
    default_queries: List[str]
    category: Literal["sports", "typing", "finance", "general"]

# Platform-specific configurations
CRICINFO_CONFIG = PlatformConfig(
    id="cricinfo",
    name="CricAPI",
    base_url="https://api.cricapi.com/v1",
    description="Comprehensive cricket statistics and live match data",
    endpoints={
        "matches": EndpointConfig(
            path="/matches",
            method="GET",
            requires_auth=True,
            rate_limit=30,  # 30 requests per minute
            params={
                "apikey": "",
                "offset": "0",
                "date": ""  # Optional date filter
            }
        ),
        "players_search": EndpointConfig(
            path="/players",
            method="GET",
            requires_auth=True,
            rate_limit=30,
            params={
                "apikey": "",
                "search": "",
                "offset": "0"
            }
        ),
        "player_stats": EndpointConfig(
            path="/players_info",
            method="GET",
            requires_auth=True,
            rate_limit=30,
            params={
                "apikey": "",
                "id": ""
            }
        ),
        "match_stats": EndpointConfig(
            path="/match_info",
            method="GET",
            requires_auth=True,
            rate_limit=30,
            params={
                "apikey": "",
                "id": ""
            }
        ),
        "series_info": EndpointConfig(
            path="/series_info",
            method="GET",
            requires_auth=True,
            rate_limit=30,
            params={
                "apikey": "",
                "id": ""
            }
        )
    },
    default_queries=[
        "Show live match scores",
        "Search for player statistics",
        "Get recent match results",
        "View series standings",
        "Compare player performances",
        "Analyze team statistics"
    ],
    category="sports"
)

TYPERACER_CONFIG = PlatformConfig(
    id="typeracer",
    name="TypeRacer",
    base_url="https://data.typeracer.com",
    description="Typing speed and accuracy statistics",
    endpoints={
        "user_stats": EndpointConfig(
            path="/games",
            params={"playerId": "", "universe": "play", "n": "100"}
        )
    },
    default_queries=[
        "Plot my typing speed over time",
        "Show accuracy vs speed correlation",
        "Analyze performance by text length"
    ],
    category="typing"
)

F1_CONFIG = PlatformConfig(
    id="f1",
    name="Formula 1",
    base_url="http://ergast.com/api/f1",
    description="Formula 1 racing statistics and results",
    endpoints={
        "current_season": EndpointConfig(
            path="/current.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,  # Ergast limits to 4 requests per second
            params={}
        ),
        "driver_standings": EndpointConfig(
            path="/current/driverStandings.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,
            params={}
        ),
        "constructor_standings": EndpointConfig(
            path="/current/constructorStandings.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,
            params={}
        ),
        "race_results": EndpointConfig(
            path="/current/results.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,
            params={"round": ""}  # Optional round number
        ),
        "qualifying_results": EndpointConfig(
            path="/current/qualifying.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,
            params={"round": ""}
        ),
        "driver_info": EndpointConfig(
            path="/drivers.json",
            method="GET",
            requires_auth=False,
            rate_limit=4,
            params={"driverId": ""}
        )
    },
    default_queries=[
        "Show current driver standings",
        "Display constructor championship points",
        "Get latest race results",
        "Compare qualifying performances",
        "Analyze driver's season progress",
        "View historical race data"
    ],
    category="sports"
)

# Registry of all supported platforms
PLATFORM_REGISTRY: Dict[str, PlatformConfig] = {
    "cricinfo": CRICINFO_CONFIG,
    "typeracer": TYPERACER_CONFIG,
    "f1": F1_CONFIG
}

def get_platform_config(platform_id: str) -> Optional[PlatformConfig]:
    """Get configuration for a specific platform"""
    return PLATFORM_REGISTRY.get(platform_id)

def list_platforms() -> List[Dict[str, str]]:
    """List all available platforms with basic info"""
    return [
        {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "category": config.category
        }
        for config in PLATFORM_REGISTRY.values()
    ] 