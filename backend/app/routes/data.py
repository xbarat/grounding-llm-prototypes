from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.database.operations import load_typing_stats
import pandas as pd

router = APIRouter()

@router.get("/load_data", tags=["Data"])
def load_data_endpoint(db: Session = Depends(get_db)) -> Dict:
    try:
        data = load_typing_stats(db)
        if not data:
            raise HTTPException(status_code=404, detail="No data found in database")
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
