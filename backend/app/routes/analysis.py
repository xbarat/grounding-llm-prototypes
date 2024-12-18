from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.utils.fetch import load_data_from_db
from app.utils.plotting import get_player_stats
from app.utils.code_utils import (
    generate_code,
    execute_code_safely,
    QueryGuidance
)

router = APIRouter()

class CodeRequest(BaseModel):
    question: str

class ExecuteRequest(BaseModel):
    code: str

@router.post("/generate_code", tags=["Analysis"])
def generate_code_endpoint(request: CodeRequest) -> Dict:
    try:
        df = load_data_from_db()
        if df is None:
            raise HTTPException(status_code=404, detail="No data found in database")
        
        code = generate_code(df, request.question)
        return {"status": "success", "code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute_code", tags=["Analysis"])
def execute_code_endpoint(request: ExecuteRequest) -> Dict:
    try:
        df = load_data_from_db()
        if df is None:
            raise HTTPException(status_code=404, detail="No data found in database")
        
        success, result, modified_code = execute_code_safely(request.code, df)
        if not success:
            raise HTTPException(status_code=400, detail=result)
        
        return {
            "status": "success",
            "result": result,
            "modified_code": modified_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/player_dashboard/{player_id}", tags=["Analysis"])
def player_dashboard(player_id: str) -> Dict:
    try:
        stats = get_player_stats(player_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Player stats not found")
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query_guidance", tags=["Analysis"])
def query_guidance() -> Dict:
    try:
        guidance = QueryGuidance()
        suggestions = guidance.filter_questions()
        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
