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
    name="ESPNCricinfo",
    base_url="https://api.cricapi.com/v1",  # We'll use CricAPI as it provides structured access
    description="Cricket statistics and live match data",
    endpoints={
        "matches": EndpointConfig(
            path="/matches",
            requires_auth=True,
            params={"apikey": ""}
        ),
        "players": EndpointConfig(
            path="/players",
            requires_auth=True,
            params={"apikey": ""}
        ),
        "stats": EndpointConfig(
            path="/stats",
            requires_auth=True,
            params={"apikey": ""}
        )
    },
    default_queries=[
        "Show batting averages of top 10 players",
        "Compare team performances in last 5 matches",
        "Analyze player strike rates in different formats"
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

# Registry of all supported platforms
PLATFORM_REGISTRY: Dict[str, PlatformConfig] = {
    "cricinfo": CRICINFO_CONFIG,
    "typeracer": TYPERACER_CONFIG
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