from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.database.operations import load_typing_stats
from app.utils.code_utils import (
    generate_code,
    extract_code_block,
    execute_code_safely,
    regenerate_code_with_error
)
import pandas as pd
import io
import base64

router = APIRouter()

class GenerateCodeRequest(BaseModel):
    query: str

class ExecuteCodeRequest(BaseModel):
    code: str

def convert_figure_to_base64(figure) -> Optional[str]:
    """Convert matplotlib figure to base64 string"""
    if figure is None:
        return None
    buf = io.BytesIO()
    figure.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@router.post("/generate_code", tags=["Analysis"])
def generate_analysis_code(
    request: GenerateCodeRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """Generate Python code for the analysis query"""
    try:
        # Load data from database
        data = load_typing_stats(db)
        if not data:
            raise HTTPException(status_code=404, detail="No data found in database")
        
        df = pd.DataFrame(data)
        
        # Generate code using Claude
        response = generate_code(df, request.query)
        code = extract_code_block(response)
        
        if not code:
            raise HTTPException(status_code=500, detail="Failed to generate valid code")
        
        return {
            "status": "success",
            "data": {
                "code": code
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute_code", tags=["Analysis"])
def execute_analysis_code(
    request: ExecuteCodeRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """Execute the generated Python code"""
    try:
        # Load data from database
        data = load_typing_stats(db)
        if not data:
            raise HTTPException(status_code=404, detail="No data found in database")
        
        df = pd.DataFrame(data)
        
        # Execute code
        success, result, code = execute_code_safely(request.code, df)
        
        if not success:
            # Try to regenerate and execute code with error context
            new_code = regenerate_code_with_error(df, "", str(result), code)
            new_code = extract_code_block(new_code)
            if new_code:
                success, result, _ = execute_code_safely(new_code, df)
        
        if not success:
            raise HTTPException(status_code=500, detail=str(result))
        
        # Convert figure to base64 if present
        figure_data = None
        if isinstance(result, dict) and result.get('figure'):
            figure_data = convert_figure_to_base64(result['figure'])
        
        return {
            "status": "success",
            "data": {
                "result": result.get('result') if isinstance(result, dict) else result,
                "figure": figure_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
