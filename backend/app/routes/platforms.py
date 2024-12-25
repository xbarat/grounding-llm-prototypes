"""
Platform routes for the GIRAFFE API.

This module provides routes for platform-specific operations like connecting users
and fetching platform data.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..utils.platform_fetcher import fetch_platform_data

router = APIRouter(prefix="/api/v1/platforms")

class Platform(BaseModel):
    id: str
    name: str
    description: str
    identifier_type: str
    example_identifier: str

class ConnectRequest(BaseModel):
    platform: str
    identifier: str

class AnalysisRequest(BaseModel):
    platform: str
    identifier: str
    query: str
    params: Optional[Dict] = None

SUPPORTED_PLATFORMS = [
    Platform(
        id="typeracer",
        name="TypeRacer",
        description="Analyze your typing performance and progress over time",
        identifier_type="username",
        example_identifier="your_typeracer_username"
    ),
    Platform(
        id="f1",
        name="Formula 1",
        description="Analyze F1 driver performance and race statistics",
        identifier_type="driver_id",
        example_identifier="max_verstappen"
    )
]

@router.get("")
async def list_platforms() -> List[Platform]:
    """List all supported platforms."""
    return SUPPORTED_PLATFORMS

@router.post("/connect")
async def connect_user(request: ConnectRequest) -> Dict:
    """Connect a user to a platform."""
    try:
        # Verify platform is supported
        if request.platform not in [p.id for p in SUPPORTED_PLATFORMS]:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")
        
        # Fetch initial data to verify connection
        if request.platform == "typeracer":
            data = await fetch_platform_data(request.platform, request.identifier, "user_stats")
        elif request.platform == "f1":
            data = await fetch_platform_data(request.platform, request.identifier, "driver_results")
        
        return {
            "status": "success",
            "message": f"Successfully connected to {request.platform}",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze")
async def analyze_data(request: AnalysisRequest) -> Dict:
    """Analyze platform data based on the provided query."""
    try:
        # Verify platform is supported
        if request.platform not in [p.id for p in SUPPORTED_PLATFORMS]:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")
        
        # Fetch and analyze data
        data = await fetch_platform_data(
            request.platform,
            request.identifier,
            request.query,
            request.params
        )
        
        return {
            "status": "success",
            "data": data,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{platform}/queries")
async def get_default_queries(platform: str) -> List[str]:
    """Get default analysis queries for a platform."""
    if platform == "typeracer":
        return [
            "Show my typing speed over time",
            "Compare my performance with global averages",
            "Analyze my accuracy trends",
            "Show my daily practice statistics"
        ]
    elif platform == "f1":
        return [
            "Show driver standings for the current season",
            "Compare qualifying performance between teammates",
            "Analyze race pace and tire management",
            "Track championship points progression"
        ]
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}") 