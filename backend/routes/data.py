from fastapi import APIRouter, HTTPException
from typing import Dict, List
from main import fetch_data, load_data_from_db

router = APIRouter()

@router.post("/fetch_data", tags=["Data"])
def fetch_data_endpoint(player_id: str, universe: str, n: int):
    try:
        data = fetch_data(player_id, universe, n)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load_data", tags=["Data"])
def load_data_endpoint():
    try:
        df = load_data_from_db()
        return {"status": "success", "columns": df.columns.tolist(), "data": df.head().to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
