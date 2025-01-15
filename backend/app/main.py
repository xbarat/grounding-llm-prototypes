"""Main application integrating F1 data pipeline with analysis"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import pandas as pd

# FastAPI and Pydantic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Database models
from app.models.user import User, QueryHistory
from app.database import get_db, SessionLocal
from sqlalchemy.orm import Session

# Custom components
from app.query.processor import QueryProcessor
from app.pipeline.data2 import DataPipeline
from app.pipeline.optimized_adapters import OptimizedQueryAdapter, OptimizedResultAdapter
from app.analyst.generate import generate_code, execute_code_safely

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    query: str

@app.post("/api/v1/analyze")
async def analyze_f1_data(request: QueryRequest) -> Dict[str, Any]:
    """
    Process F1 data analysis queries using the optimized pipeline.
    
    Args:
        request: QueryRequest containing the natural language query
        
    Returns:
        Dict containing analysis results, executed code, and processing metadata
    """
    try:
        # Record start time for performance tracking
        start_time = datetime.now()
        
        # Step 1: Process query
        processor = QueryProcessor()
        query_result = await processor.process_query(request.query)
        
        # Step 2: Adapt query using optimized adapter
        query_adapter = OptimizedQueryAdapter()
        adapted_result = await query_adapter.adapt(query_result)
        
        # Step 3: Process through optimized pipeline
        pipeline = DataPipeline()
        requirements = adapted_result.to_data_requirements()
        pipeline_response = await pipeline.process(requirements)
        
        # Step 4: Adapt pipeline result
        result_adapter = OptimizedResultAdapter()
        pipeline_result = await result_adapter.adapt_pipeline_result(pipeline_response, start_time)
        
        if not pipeline_result.success or not pipeline_result.data:
            raise HTTPException(
                status_code=400,
                detail=f"Pipeline processing failed: {pipeline_result.error or 'No data returned'}"
            )
            
        # Step 5: Generate and execute analysis code
        results = pipeline_result.data.get('results', {})
        df = pd.DataFrame(results) if results else pd.DataFrame()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available for analysis")
        code = generate_code(df, request.query)
        success, result, executed_code = execute_code_safely(code, df)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Code execution failed: {result}"
            )
            
        # Return comprehensive result
        return {
            "success": True,
            "data": result,
            "executed_code": executed_code,
            "query_trace": query_result.trace,
            "processing_time": (datetime.now() - start_time).total_seconds(),
            "metadata": pipeline_result.metadata
        }
        
    except HTTPException as e:
        # Handle HTTP exceptions separately to preserve status code
        return {
            "success": False,
            "error": "Analysis failed",
            "details": e.detail,
            "processing_time": (datetime.now() - start_time).total_seconds()
        }
    except Exception as e:
        # Handle other exceptions
        return {
            "success": False,
            "error": "Analysis failed",
            "details": str(e),
            "processing_time": (datetime.now() - start_time).total_seconds()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 