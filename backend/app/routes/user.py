from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.database.operations import save_typing_stats
from app.utils.fetch import fetch_user_stats, fetch_data

router = APIRouter()

class UserRequest(BaseModel):
    username: str

class FetchDataRequest(BaseModel):
    player_id: str
    universe: str = "play"
    n: int = 100
    before_id: Optional[str] = None

@router.post("/connect_user", tags=["User"])
def connect_user(request: UserRequest) -> Dict:
    try:
        user_stats = fetch_user_stats(request.username)
        if not user_stats:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "data": user_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch_data", tags=["User"])
def fetch_user_data(
    request: FetchDataRequest,
    db: Session = Depends(get_db)
) -> Dict:
    try:
        data = fetch_data(
            request.player_id,
            request.universe,
            request.n,
            request.before_id
        )
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Save data to database
        save_typing_stats(db, data, request.player_id)
        
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))