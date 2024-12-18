from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Optional, List
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
def query_guidance(
    level: Optional[str] = Query(None, description="Filter questions by level"),
    category: Optional[str] = Query(None, description="Filter questions by category"),
    query: Optional[str] = Query(None, description="Search query to find relevant questions"),
    max_suggestions: Optional[int] = Query(5, description="Maximum number of suggestions to return")
) -> Dict:
    """Get suggested questions for analysis, optionally filtered by level, category, and search query"""
    try:
        guidance = QueryGuidance()
        
        # Get available levels and categories
        levels = guidance.get_levels()
        categories = guidance.get_categories()
        
        # Validate level if provided
        if level and level not in levels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid level. Available levels: {', '.join(levels)}"
            )
        
        # Validate category if provided
        if category and category not in categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Available categories: {', '.join(categories)}"
            )
        
        # Validate max_suggestions
        if max_suggestions < 1:
            raise HTTPException(
                status_code=400,
                detail="max_suggestions must be greater than 0"
            )
        
        # Get filtered and scored questions
        questions = guidance.filter_questions(
            level=level,
            category=category,
            query=query,
            max_suggestions=max_suggestions
        )
        
        return {
            "status": "success",
            "metadata": {
                "available_levels": levels,
                "available_categories": categories,
                "filters_applied": {
                    "level": level,
                    "category": category,
                    "query": query,
                    "max_suggestions": max_suggestions
                }
            },
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
