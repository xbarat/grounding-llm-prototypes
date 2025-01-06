"""Main application integrating F1 data pipeline with analysis"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from app.pipeline.data2 import DataPipeline, DataRequirements, DataResponse
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely
import re
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.auth.routes import router as auth_router
from app.models.user import User, QueryHistory
from app.auth.utils import get_current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="F1 Data Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Request/Response Models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    detail: Optional[str] = None

async def analyze_f1_data(query: str, requirements: DataRequirements) -> Dict[str, Any]:
    """Process an F1 query from data retrieval through analysis"""
    try:
        # Log request details
        logger.info(f"Processing query: {query}")
        logger.info(f"Endpoint: {requirements.endpoint}")
        logger.info(f"Parameters: {requirements.params}")
        
        # Step 1: Get data from pipeline
        pipeline = DataPipeline()
        logger.info("Fetching data from pipeline...")
        response = await pipeline.process(requirements)
        
        if not response.success or not response.data:
            logger.error(f"Pipeline error: {response.error}")
            return {
                "success": False,
                "error": "Failed to retrieve data",
                "details": response.error
            }
            
        logger.info(f"Data retrieved successfully. Shape: {pd.DataFrame(response.data['results']).shape}")
        
        # Step 2: Generate analysis code
        logger.info("Generating analysis code...")
        code_response = generate_code(response.data["results"], query)
        code = extract_code_block(code_response)
        
        if not code:
            logger.error("No code block found in response")
            return {
                "success": False,
                "error": "Failed to generate code",
                "details": "No code block found in response"
            }
            
        logger.info("Code generated successfully")
        
        # Step 3: Execute analysis
        logger.info("Executing analysis code...")
        success, result, modified_code = execute_code_safely(code, response.data["results"])
        
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
            "code": modified_code
        }
        
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        return {
            "success": False,
            "error": "Analysis failed",
            "details": str(e)
        }

def get_requirements_for_query(query: str) -> DataRequirements:
    """Get appropriate DataRequirements based on the query"""
    query = query.lower()
    logger.info(f"Generating requirements for query: {query}")
    
    # Extract year ranges using regex patterns
    years = []
    # Pattern 1: "YYYY-YYYY" (e.g., "2021-2023")
    year_range_match = re.search(r'(\d{4})-(\d{4})', query)
    if year_range_match:
        start_year = int(year_range_match.group(1))
        end_year = int(year_range_match.group(2))
        years = [str(year) for year in range(start_year, end_year + 1)]
        logger.info(f"Year range detected: {start_year} to {end_year}")
    # Pattern 2: "from YYYY to YYYY" or "YYYY to YYYY"
    elif "to" in query:
        # Try to find two years around "to"
        year_pattern = r'(\d{4}).*?to.*?(\d{4})'
        to_match = re.search(year_pattern, query)
        if to_match:
            start_year = int(to_match.group(1))
            end_year = int(to_match.group(2))
            years = [str(year) for year in range(start_year, end_year + 1)]
            logger.info(f"Year range detected: {start_year} to {end_year}")
    
    # Default parameters
    params = {"season": years if years else ["2023"]}  # Always use list for seasons
    endpoint = "/api/f1/drivers"
    
    # Extract driver name if present
    for driver, api_id in {
        "max verstappen": "max_verstappen",
        "lewis hamilton": "hamilton",
        "charles leclerc": "leclerc",
        "fernando alonso": "alonso",
        "lando norris": "norris",
        "george russell": "russell",
    }.items():
        if driver in query:
            params["driver"] = [api_id]  # Use list for driver
            logger.info(f"Driver found: {driver} -> {api_id}")
            break
    
    # Check for constructor queries
    if "red bull" in query:
        endpoint = "/api/f1/constructors"
        params["constructor"] = ["red_bull"]  # Use list for constructor
        logger.info("Constructor: Red Bull")
    elif "mercedes" in query:
        endpoint = "/api/f1/constructors"
        params["constructor"] = ["mercedes"]  # Use list for constructor
        logger.info("Constructor: Mercedes")
    
    requirements = DataRequirements(endpoint=endpoint, params=params)
    logger.info(f"Generated requirements: {requirements}")
    return requirements

async def test_analysis():
    """Test the integrated analysis pipeline with all test queries"""
    test_queries = [
        # Basic performance queries
        "How has Max Verstappen performed in the 2023 season?",
        "What are Lewis Hamilton's stats for 2023?",
        
        # Qualifying specific queries
        "What was Charles Leclerc's qualifying position in Monaco 2023?",
        "Show me Oscar Piastri's qualifying results for 2023",
        
        # Race performance queries
        "How many podiums did Fernando Alonso get in 2023?",
        "What's Lando Norris's average finishing position in 2023?",
        
        # Circuit specific queries
        "How did George Russell perform at Silverstone in 2023?",
        "Show me Carlos Sainz's results at Monza 2023"
    ]
    
    print("\nStarting F1 Data Analysis Test Suite...")
    print("=" * 80)
    logger.info("Starting test suite with 8 queries")
    
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/8: {query}")
        print("-" * 40)
        logger.info(f"Running test {i}/8: {query}")
        
        requirements = get_requirements_for_query(query)
        result = await analyze_f1_data(query, requirements)
        results.append((query, result))
        
        if result["success"]:
            logger.info(f"Test {i} successful")
            print("✓ Success!")
            if result["data"].get("output"):
                print("\nOutput:")
                print(result["data"]["output"].strip())
        else:
            logger.error(f"Test {i} failed: {result['error']}")
            print("✗ Failed!")
            print("Error:", result["error"])
            print("Details:", result["details"])
            
        print("-" * 40)
    
    # Print summary
    print("\nTest Summary")
    print("=" * 80)
    successes = sum(1 for _, r in results if r["success"])
    logger.info(f"Test suite completed. Success rate: {successes}/8")
    print(f"Total queries: 8")
    print(f"Successful: {successes}")
    print(f"Failed: {8 - successes}")
    
    # Print failed queries if any
    if successes < 8:
        print("\nFailed Queries:")
        for query, result in results:
            if not result["success"]:
                print(f"- {query}")
                print(f"  Error: {result['error']}")
                logger.error(f"Failed query: {query}")
                logger.error(f"Error details: {result['details']}")

# API Endpoints
@app.post("/api/v1/process_query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query and return data requirements"""
    try:
        requirements = get_requirements_for_query(request.query)
        return {
            "status": "success",
            "data": {
                "endpoint": requirements.endpoint,
                "params": requirements.params
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
        
        if not response.success or not response.data:
            return {
                "status": "error",
                "detail": response.error or "No data returned"
            }
            
        # Convert DataFrame to dictionary
        serialized_data = {}
        for key, df in response.data.items():
            if isinstance(df, pd.DataFrame):
                serialized_data[key] = df.to_dict(orient='records')
            else:
                serialized_data[key] = df
            
        return {
            "status": "success",
            "data": serialized_data
        }
    except Exception as e:
        logger.exception("Error fetching data")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_data", response_model=QueryResponse)
async def analyze_data(request: Dict[str, Any]):
    """Generate analysis and visualization from F1 data"""
    try:
        query = request.get("query")
        data = request.get("data")
        requirements = request.get("requirements", {})
        
        if not all([query, data, requirements]):
            raise ValueError("Missing required fields")
        
        if not isinstance(query, str):
            raise ValueError("Query must be a string")
            
        endpoint = requirements.get("endpoint")
        params = requirements.get("params", {})
        
        if not endpoint:
            raise ValueError("Missing endpoint in requirements")

        # Special handling for follow-up queries
        if endpoint == '/api/f1/follow-up':
            logger.info("Processing follow-up query...")
            # Convert the existing data back to DataFrame
            df = pd.DataFrame.from_records(data.get("results", []))
            if df.empty:
                return {
                    "status": "error",
                    "detail": "No data available for follow-up analysis"
                }

            # Generate analysis code for the follow-up query
            logger.info("Generating follow-up analysis code...")
            code_response = generate_code(df, query, is_follow_up=True)
            code = extract_code_block(code_response)
            
            if not code:
                logger.error("No code block found in follow-up response")
                return {
                    "status": "error",
                    "detail": "Failed to generate follow-up analysis"
                }
            
            # Execute the follow-up analysis
            logger.info("Executing follow-up analysis code...")
            success, result, modified_code = execute_code_safely(code, df)
            
            if not success:
                logger.error(f"Follow-up code execution failed: {result}")
                return {
                    "status": "error",
                    "detail": result
                }
            
            return {
                "status": "success",
                "data": {
                    "summary": result.get("output"),
                    "visualization": result.get("figure"),
                    "data": result.get("data"),
                    "rawData": data
                }
            }
            
        # Regular query processing
        requirements_obj = DataRequirements(
            endpoint=endpoint,
            params=params
        )
            
        result = await analyze_f1_data(query, requirements_obj)
        
        if not result["success"]:
            return {
                "status": "error",
                "detail": result["error"]
            }
            
        return {
            "status": "success",
            "data": {
                "summary": result["data"].get("output"),
                "visualization": result["data"].get("figure"),
                "data": result["data"].get("data"),
                "rawData": data
            }
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
        # Get request body
        body = await request.json()
        
        # Create new query history entry
        query_history = QueryHistory(
            user_id=current_user.id,
            query=body.get('query'),
            result=body.get('data', {}),
            parent_id=body.get('parent_id')  # Get parent_id if this is a follow-up query
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
async def get_query_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get user's query history"""
    try:
        # Get only root queries (those without parent_id)
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

if __name__ == "__main__":
    asyncio.run(test_analysis()) 