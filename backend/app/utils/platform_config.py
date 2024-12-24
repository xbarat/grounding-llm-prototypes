from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class EndpointConfig(BaseModel):
    path: str
    method: str = "GET"
    params: Dict[str, Any] = {}
    requires_auth: bool = False
    rate_limit: Optional[int] = None

class PlatformConfig(BaseModel):
    id: str
    name: str
    description: str
    base_url: str
    endpoints: Dict[str, EndpointConfig]
    default_queries: List[str]

PLATFORM_CONFIGS: Dict[str, PlatformConfig] = {
    "typeracer": PlatformConfig(
        id="typeracer",
        name="TypeRacer",
        description="Competitive typing platform",
        base_url="https://data.typeracer.com/",
        endpoints={
            "user_stats": EndpointConfig(
                path="users?id={playerId}",
                method="GET"
            )
        },
        default_queries=[
            "Show my typing speed over time",
            "Compare my accuracy with the global average",
            "Analyze my performance by time of day"
        ]
    ),
    "f1": PlatformConfig(
        id="f1",
        name="Formula 1",
        description="Formula 1 Racing Statistics and Analysis",
        base_url="http://ergast.com/api/f1",
        endpoints={
            "driver_standings": EndpointConfig(
                path="/current/driverStandings.json",
                method="GET",
                rate_limit=30
            ),
            "race_results": EndpointConfig(
                path="/{year}/results.json",
                method="GET",
                rate_limit=30
            ),
            "qualifying_results": EndpointConfig(
                path="/{year}/qualifying.json",
                method="GET",
                rate_limit=30
            ),
            "driver_info": EndpointConfig(
                path="/drivers/{driverId}.json",
                method="GET",
                rate_limit=30
            ),
            "constructor_standings": EndpointConfig(
                path="/{year}/constructorStandings.json",
                method="GET",
                rate_limit=30
            )
        },
        default_queries=[
            "Compare Max Verstappen and Lewis Hamilton's performance in the last 5 races",
            "Show the correlation between qualifying position and race finish for Ferrari drivers",
            "Analyze Red Bull's performance trend across the season",
            "Plot the points progression of the top 3 drivers",
            "Show the distribution of DNFs by constructor",
            "Compare pit stop strategies between Mercedes and Red Bull",
            "Visualize the qualifying gap between teammates",
            "Plot the championship points gap over time",
            "Analyze overtaking positions on each circuit",
            "Show the impact of grid position on race finish position"
        ]
    )
}

def list_platforms() -> List[Dict[str, str]]:
    """List all available platforms"""
    return [
        {
            "id": config.id,
            "name": config.name,
            "description": config.description
        }
        for config in PLATFORM_CONFIGS.values()
    ]

def get_platform_config(platform_id: str) -> Optional[PlatformConfig]:
    """Get configuration for a specific platform"""
    return PLATFORM_CONFIGS.get(platform_id) 