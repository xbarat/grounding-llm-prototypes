"""Main application integrating F1 data pipeline with analysis"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from app.pipeline.data2 import DataPipeline, DataRequirements, DataResponse
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="F1 Data Analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
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
    
    # Extract year ranges
    years = []
    if "from" in query and "to" in query:
        try:
            start_year = int(query.split("from")[1].split("to")[0].strip())
            end_year = int(query.split("to")[1].split()[0].strip())
            years = [str(year) for year in range(start_year, end_year + 1)]
            logger.info(f"Year range detected: {start_year} to {end_year}")
        except ValueError:
            years = ["2023"]  # Default to current season if parsing fails
    
    # Default parameters
    params = {"season": years if years else "2023"}
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
            params["driver"] = api_id
            logger.info(f"Driver found: {driver} -> {api_id}")
            break
    
    # Check for constructor queries
    if "red bull" in query:
        endpoint = "/api/f1/constructors"
        params["constructor"] = "red_bull"
        logger.info("Constructor: Red Bull")
    elif "mercedes" in query:
        endpoint = "/api/f1/constructors"
        params["constructor"] = "mercedes"
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
async def save_query_history(request: Dict[str, Any]):
    """Save query and results to history"""
    try:
        # For now, just log the query and return success
        # In a real implementation, this would save to a database
        logger.info(f"Saving query to history: {request.get('query')}")
        return {
            "status": "success",
            "data": {"saved": True}
        }
    except Exception as e:
        logger.exception("Error saving query history")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    asyncio.run(test_analysis()) 