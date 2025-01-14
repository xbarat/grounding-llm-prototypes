"""Main application integrating F1 data pipeline with analysis"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
try:
    from fastapi import FastAPI, HTTPException, Depends, Request, Body
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    print("FastAPI dependencies not found. Install with: pip install fastapi uvicorn")
    raise

from sqlalchemy.orm import Session
from app.pipeline.data2 import DataPipeline
from app.query.models import DataRequirements
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely
from app.database import get_db
from app.auth.utils import get_current_user
from app.models.user import User, QueryHistory
from .query.processor import QueryProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="F1 Data Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    detail: Optional[str] = None

async def analyze_f1_data(query: str) -> Dict[str, Any]:
    """Process an F1 query from data retrieval through analysis"""
    try:
        # Log request details
        logger.info(f"Processing query: {query}")
        
        # Step 1: Process query to get requirements
        processor = QueryProcessor()
        processing_result = await processor.process_query(query)
        requirements = processing_result.requirements
        
        logger.info(f"Query processed. Endpoint: {requirements.endpoint}")
        logger.info(f"Parameters: {requirements.params}")
        
        # Step 2: Get data from pipeline
        pipeline = DataPipeline()
        logger.info("Fetching data from pipeline...")
        response = await pipeline.process(requirements)
        
        if not isinstance(response, dict) or not response.get("results"):
            logger.error(f"Pipeline error: {response.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": "Failed to retrieve data",
                "details": response.get("error", "No data returned")
            }
            
        logger.info(f"Data retrieved successfully. Shape: {pd.DataFrame(response['results']).shape}")
        
        # Step 3: Generate analysis code
        logger.info("Generating analysis code...")
        code_response = generate_code(response["results"], query)
        code = extract_code_block(code_response)
        
        if not code:
            logger.error("No code block found in response")
            return {
                "success": False,
                "error": "Failed to generate code",
                "details": "No code block found in response"
            }
            
        logger.info("Code generated successfully")
        
        # Step 4: Execute analysis
        logger.info("Executing analysis code...")
        success, result, modified_code = execute_code_safely(code, response["results"])
        
        if not success:
            logger.error(f"Code execution failed: {result}")
            return {
                "success": False,
                "error": "Analysis execution failed",
                "details": result
            }
            
        logger.info("Analysis completed successfully")
        return {
            "success": True,
            "data": result,
            "code": modified_code,
            "query_trace": processing_result.trace if hasattr(processing_result, 'trace') else None
        }
        
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        return {
            "success": False,
            "error": "Analysis failed",
            "details": str(e)
        }

# Essential API Routes for Frontend Integration
@app.post("/api/v1/process_query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query and return data requirements"""
    try:
        processor = QueryProcessor()
        processing_result = await processor.process_query(request.query)
        return {
            "status": "success",
            "data": {
                "endpoint": processing_result.requirements.endpoint,
                "params": processing_result.requirements.params
            }
        }
    except Exception as e:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fetch_data", response_model=QueryResponse)
async def fetch_data(requirements: DataRequirements):
    """Fetch F1 data based on requirements"""
    try:
        pipeline = DataPipeline()
        response = await pipeline.process(requirements)
        
        if not isinstance(response, dict) or not response.get("results"):
            return {
                "status": "error",
                "detail": response.get("error", "No data returned")
            }
            
        return {
            "status": "success",
            "data": {"results": response["results"]}
        }
    except Exception as e:
        logger.exception("Error fetching data")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_data", response_model=QueryResponse)
async def analyze_data(request: Request):
    """Generate analysis and visualization from F1 data"""
    try:
        body = await request.json()
        query = body.get("query")
        data = body.get("data")
        
        if not query or not data:
            raise ValueError("Missing query or data")
            
        result = await analyze_f1_data(query)
        
        if not result["success"]:
            return {
                "status": "error",
                "detail": result["error"]
            }
            
        return {
            "status": "success",
            "data": result["data"]
        }
    except Exception as e:
        logger.exception("Error analyzing data")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/query_history", response_model=QueryResponse)
async def save_query_history(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save query and results to history"""
    try:
        body = await request.json()
        query_history = QueryHistory(
            user_id=current_user.id,
            query=body.get('query'),
            result=body.get('data', {}),
            parent_id=body.get('parent_id')
        )
        db.add(query_history)
        db.commit()
        db.refresh(query_history)

        return {
            "status": "success",
            "data": {"saved": True}
        }
    except Exception as e:
        logger.exception("Error saving query history")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/query_history", response_model=QueryResponse)
async def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's query history"""
    try:
        root_queries = db.query(QueryHistory).filter(
            QueryHistory.user_id == current_user.id,
            QueryHistory.parent_id.is_(None)
        ).order_by(QueryHistory.created_at.desc()).all()
        
        return {
            "status": "success",
            "data": {
                "queries": [
                    {
                        "id": str(q.id),
                        "title": q.query,
                        "thread": [
                            {
                                "id": str(thread_q.id),
                                "query": thread_q.query,
                                "result": thread_q.result,
                                "timestamp": thread_q.created_at.isoformat()
                            } for thread_q in [q] + q.follow_ups
                        ],
                        "timestamp": q.created_at.isoformat()
                    } for q in root_queries
                ]
            }
        }
    except Exception as e:
        logger.exception("Error fetching query history")
        raise HTTPException(status_code=500, detail=str(e))

# Simple health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

async def test_analysis():
    """Test the integrated analysis pipeline"""
    logger.info("\nStarting F1 Data Analysis Test Suite...")
    
    test_queries = [
        "How has Max Verstappen performed in the 2023 season?",
        "Compare Verstappen and Perez's performance in wet races during 2023"
    ]
    
    total_queries = len(test_queries)
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\nTest {i}/{total_queries}: {query}")
        try:
            result = await analyze_f1_data(query)
            if result["success"]:
                logger.info("✓ Success!")
                successful_queries += 1
                logger.info(f"Output: {result['data'].get('output', 'No output')}")
            else:
                logger.error(f"✗ Failed: {result['error']}")
                logger.error(f"Details: {result['details']}")
        except Exception as e:
            logger.error(f"✗ Error processing query: {str(e)}")
    
    success_rate = (successful_queries / total_queries) * 100
    logger.info(f"\nTest Summary:")
    logger.info(f"Total Queries: {total_queries}")
    logger.info(f"Successful: {successful_queries}")
    logger.info(f"Failed: {total_queries - successful_queries}")
    logger.info(f"Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_analysis()) 