from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.utils.fetch import load_data_from_db
import pandas as pd

router = APIRouter()

@router.get("/load_data", tags=["Data"])
def load_data_endpoint() -> Dict:
    try:
        df = load_data_from_db()
        if df is None:
            raise HTTPException(status_code=404, detail="No data found in database")
        return {
            "status": "success",
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
