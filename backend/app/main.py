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

# Set up logging with more detail
logging.basicConfig(level=logging.DEBUG)
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
        start_time = datetime.now().timestamp()
        logger.debug(f"Starting analysis with query: {request.query}")
        
        # Step 1: Process query
        processor = QueryProcessor()
        query_result = await processor.process_query(request.query)
        logger.debug(f"Query processing result: {query_result}")
        
        # Step 2: Adapt query using optimized adapter
        query_adapter = OptimizedQueryAdapter()
        adapted_result = await query_adapter.adapt(query_result)
        logger.debug(f"Adapted query result: {adapted_result}")
        
        # Step 3: Process through optimized pipeline
        pipeline = DataPipeline()
        requirements = adapted_result.to_data_requirements()
        pipeline_response = await pipeline.process(requirements)
        logger.debug(f"Pipeline response type: {type(pipeline_response)}")
        
        # Step 4: Adapt pipeline result
        result_adapter = OptimizedResultAdapter()
        pipeline_result = await result_adapter.adapt_pipeline_result(pipeline_response, start_time)
        logger.debug(f"Pipeline result success: {pipeline_result.success}")
        
        if not pipeline_result.success or pipeline_result.data is None:
            logger.error(f"Pipeline failed: {pipeline_result.error}")
            raise HTTPException(
                status_code=400,
                detail=f"Pipeline processing failed: {pipeline_result.error or 'No data returned'}"
            )
            
        # Step 5: Generate and execute analysis code
        results = pipeline_result.data.get('results', {})
        logger.debug(f"Raw results: {results}")
        
        try:
            # Create DataFrame and normalize the ConstructorTable column
            if isinstance(results, dict):
                df = pd.DataFrame([results])
            elif isinstance(results, list):
                df = pd.DataFrame(results)
            else:
                df = pd.DataFrame(results)
                
            # Normalize the ConstructorTable column if it exists and contains nested data
            if 'ConstructorTable' in df.columns:
                # Extract Ferrari's data from each year
                df['constructor_data'] = df['ConstructorTable'].apply(
                    lambda x: next((item for item in x if item['constructorId'] == 'ferrari'), {}) 
                    if isinstance(x, list) else {}
                )
                
                # Drop the original ConstructorTable column
                df = df.drop('ConstructorTable', axis=1)
                
                # If we have constructor data, expand it into separate columns
                if not df['constructor_data'].empty:
                    constructor_df = pd.json_normalize(df['constructor_data'].iloc[0])
                    df = pd.concat([df.drop('constructor_data', axis=1), constructor_df], axis=1)
            
            logger.debug(f"DataFrame creation successful")
            logger.debug(f"DataFrame shape: {df.shape}")
            logger.debug(f"DataFrame columns: {list(df.columns)}")
            logger.debug(f"First few rows: {df.head()}")
            
            if df.empty:
                raise HTTPException(status_code=400, detail="DataFrame is empty after creation")
                
        except Exception as e:
            logger.error(f"DataFrame creation error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create DataFrame: {str(e)}")
        
        # Generate and execute code with additional logging
        logger.debug("Generating analysis code")
        code = generate_code(df, request.query)
        logger.debug(f"Generated code: {code}")
        
        success, result, executed_code = execute_code_safely(code, df)
        logger.debug(f"Code execution success: {success}")
        
        if not success:
            logger.error(f"Code execution failed: {result}")
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
            "processing_time": datetime.now().timestamp() - start_time,
            "metadata": pipeline_result.metadata
        }
        
    except HTTPException as e:
        logger.error(f"HTTP Exception: {str(e)}")
        return {
            "success": False,
            "error": "Analysis failed",
            "details": e.detail,
            "processing_time": datetime.now().timestamp() - start_time
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": "Analysis failed",
            "details": str(e),
            "processing_time": datetime.now().timestamp() - start_time
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 