from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from main import fetch_user_stats  # Existing logic from Streamlit MVP

router = APIRouter()

class UserRequest(BaseModel):
    username: str

@router.post("/connect_user", tags=["User"])
def connect_user(request: UserRequest) -> Dict:
    try:
        user_stats = fetch_user_stats(request.username)
        if not user_stats:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "data": user_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
