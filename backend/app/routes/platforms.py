from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel
from ..utils.platform_config import list_platforms, get_platform_config
from ..utils.platform_fetcher import (
    PlatformFetcher,
    RateLimitError,
    AuthenticationError,
    DataFetchError
)

router = APIRouter()

class PlatformDataRequest(BaseModel):
    platform_id: str
    endpoint: str
    params: Optional[Dict] = None

@router.get("/platforms", tags=["Platforms"])
async def get_available_platforms() -> Dict:
    """Get list of available data platforms"""
    try:
        platforms = list_platforms()
        return {
            "status": "success",
            "data": {
                "platforms": platforms
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform_id}/queries", tags=["Platforms"])
async def get_platform_queries(platform_id: str) -> Dict:
    """Get default queries for a specific platform"""
    try:
        fetcher = PlatformFetcher(platform_id)
        queries = fetcher.get_default_queries()
        return {
            "status": "success",
            "data": {
                "queries": queries
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/platforms/fetch", tags=["Platforms"])
async def fetch_platform_data(request: PlatformDataRequest) -> Dict:
    """Fetch data from a specific platform endpoint"""
    try:
        fetcher = PlatformFetcher(request.platform_id)
        data = fetcher.fetch_data(request.endpoint, request.params)
        return {
            "status": "success",
            "data": data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DataFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cricket-specific endpoints
@router.get("/platforms/cricket/matches", tags=["Cricket"])
async def get_cricket_matches(date: Optional[str] = None) -> Dict:
    """Get cricket matches data"""
    try:
        fetcher = PlatformFetcher("cricinfo")
        data = fetcher.fetch_data("matches", {"date": date} if date else None)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/cricket/player/{player_id}", tags=["Cricket"])
async def get_player_stats(player_id: str) -> Dict:
    """Get cricket player statistics"""
    try:
        fetcher = PlatformFetcher("cricinfo")
        data = fetcher.fetch_data("players", {"id": player_id})
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 