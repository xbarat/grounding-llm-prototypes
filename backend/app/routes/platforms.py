from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel
from ..utils.platform_config import list_platforms, get_platform_config
from ..utils.platform_fetcher import (
    PlatformFetcher,
    RateLimitError,
    AuthenticationError,
    DataFetchError,
    fetch_f1_driver_comparison,
    fetch_f1_qualifying_analysis
)
from ..utils.code_utils import generate_code, execute_code_safely
import pandas as pd
import io
import base64

router = APIRouter()

class PlatformDataRequest(BaseModel):
    platform_id: str
    endpoint: str
    params: Optional[Dict] = None

class AnalysisRequest(BaseModel):
    platform_id: str
    query: str
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

@router.post("/platforms/analyze", tags=["Analysis"])
async def analyze_platform_data(request: AnalysisRequest) -> Dict:
    """Generate and execute analysis code based on natural language query"""
    try:
        fetcher = PlatformFetcher(request.platform_id)
        
        # Fetch appropriate data based on the query
        if request.platform_id == "f1":
            # Determine the type of data needed based on the query
            if "qualifying" in request.query.lower():
                df = await fetcher.fetch_f1_data("qualifying_results", request.params)
            elif "standings" in request.query.lower():
                df = await fetcher.fetch_f1_data("driver_standings", request.params)
            else:
                df = await fetcher.fetch_f1_data("race_results", request.params)
        else:
            # Handle other platforms
            data = await fetcher.fetch_data(request.endpoint, request.params)
            df = pd.DataFrame(data)

        # Generate analysis code
        code_response = generate_code(df, request.query)
        if not code_response:
            raise HTTPException(status_code=500, detail="Failed to generate analysis code")

        # Execute the generated code
        success, result, modified_code = execute_code_safely(code_response, df)
        
        if not success:
            raise HTTPException(status_code=500, detail=str(result))

        # Convert figure to base64 if present
        figure_data = None
        if isinstance(result, dict) and result.get('figure'):
            buf = io.BytesIO()
            result['figure'].savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            figure_data = base64.b64encode(buf.getvalue()).decode('utf-8')

        return {
            "status": "success",
            "data": {
                "result": result.get('result') if isinstance(result, dict) else result,
                "figure": figure_data,
                "code": modified_code
            }
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

@router.post("/platforms/fetch", tags=["Platforms"])
async def fetch_platform_data(request: PlatformDataRequest) -> Dict:
    """Fetch data from a specific platform endpoint"""
    try:
        fetcher = PlatformFetcher(request.platform_id)
        data = await fetcher.fetch_data(request.endpoint, request.params)
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

# F1-specific endpoints
@router.get("/platforms/f1/standings", tags=["Formula 1"])
async def get_f1_standings(category: str = "driver") -> Dict:
    """Get F1 standings (driver or constructor)"""
    try:
        fetcher = PlatformFetcher("f1")
        endpoint = "driver_standings" if category == "driver" else "constructor_standings"
        data = fetcher.fetch_data(endpoint)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/f1/races", tags=["Formula 1"])
async def get_race_results(round: Optional[int] = None) -> Dict:
    """Get F1 race results"""
    try:
        fetcher = PlatformFetcher("f1")
        params = {"round": str(round)} if round else None
        data = fetcher.fetch_data("race_results", params)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/f1/qualifying/{round}", tags=["Formula 1"])
async def get_qualifying_results(round: int) -> Dict:
    """Get F1 qualifying results for a specific round"""
    try:
        fetcher = PlatformFetcher("f1")
        data = fetcher.fetch_data("qualifying_results", {"round": str(round)})
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/f1/driver/{driver_id}", tags=["Formula 1"])
async def get_driver_info(driver_id: str) -> Dict:
    """Get F1 driver information"""
    try:
        fetcher = PlatformFetcher("f1")
        data = fetcher.fetch_data("driver_info", {"driverId": driver_id})
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 