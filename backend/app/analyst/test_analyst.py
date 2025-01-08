"""Integration tests for analyst module using query processor and pipeline stages"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback
import os
import json
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline
from app.query.processor import QueryProcessor
from app.pipeline.optimized_adapters import (
    OptimizedQueryAdapter,
    OptimizedResultAdapter,
    OptimizedValidationAdapter
)
from app.analyst.generate import generate_code, extract_code_block, execute_code_safely
from tests.test_queries import TestQueries

class AnalystMetrics:
    """Tracks metrics for analyst testing"""
    def __init__(self):
        self.total_queries = 0
        self.code_generation_success = 0
        self.code_generation_failure = 0
        self.execution_success = 0
        self.execution_failure = 0
        self.visualization_success = 0
        self.visualization_failure = 0
        self.processing_times: List[float] = []
        self.errors: List[Dict[str, Any]] = []
        
    def record_code_generation_success(self):
        self.code_generation_success += 1
        
    def record_code_generation_failure(self, error: str):
        self.code_generation_failure += 1
        self.errors.append({
            'stage': 'code_generation',
            'error': error
        })
        
    def record_execution_success(self):
        self.execution_success += 1
        
    def record_execution_failure(self, error: str):
        self.execution_failure += 1
        self.errors.append({
            'stage': 'execution',
            'error': error
        })
        
    def record_visualization_success(self):
        self.visualization_success += 1
        
    def record_visualization_failure(self, error: str):
        self.visualization_failure += 1
        self.errors.append({
            'stage': 'visualization',
            'error': error
        })
        
    def record_processing_time(self, time: float):
        self.processing_times.append(time)
        
    def print_summary(self):
        """Print test metrics summary"""
        total_queries = self.code_generation_success + self.code_generation_failure
        self.total_queries = total_queries
        
        print("\n=== Analyst Test Results ===")
        
        print("\nCode Generation:")
        if total_queries > 0:
            print(f"  Success: {self.code_generation_success}/{total_queries} ({self.code_generation_success/total_queries*100:.1f}%)")
            print(f"  Failure: {self.code_generation_failure}/{total_queries} ({self.code_generation_failure/total_queries*100:.1f}%)")
        else:
            print("  No queries processed")
        
        print("\nCode Execution:")
        if total_queries > 0:
            print(f"  Success: {self.execution_success}/{total_queries} ({self.execution_success/total_queries*100:.1f}%)")
            print(f"  Failure: {self.execution_failure}/{total_queries} ({self.execution_failure/total_queries*100:.1f}%)")
        else:
            print("  No code executed")
        
        print("\nVisualization Generation:")
        if total_queries > 0:
            print(f"  Success: {self.visualization_success}/{total_queries} ({self.visualization_success/total_queries*100:.1f}%)")
            print(f"  Failure: {self.visualization_failure}/{total_queries} ({self.visualization_failure/total_queries*100:.1f}%)")
        else:
            print("  No visualizations generated")
        
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        print(f"\nPerformance:")
        print(f"  Average Processing Time: {avg_time:.2f} seconds")
        print(f"  Total Tests Run: {total_queries}")
        
        if self.errors:
            print("\nErrors Encountered:")
            for error in self.errors:
                print(f"  - [{error['stage']}] {error['error']}")

async def make_api_request(client: httpx.AsyncClient, url: str, params: Dict[str, Any], max_retries: int = 3) -> str:
    """Make API request with retries"""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.text
        except httpx.TimeoutException as e:
            last_error = e
            if attempt == max_retries - 1:
                break
            print(f"\nTimeout on attempt {attempt + 1}, retrying...")
            await asyncio.sleep(1)  # Wait before retry
        except Exception as e:
            last_error = e
            if attempt == max_retries - 1:
                break
            print(f"\nError on attempt {attempt + 1}: {str(e)}, retrying...")
            await asyncio.sleep(1)
    
    raise last_error or Exception("Failed to make API request after all retries")

async def test_analyst_pipeline(query: str, client: httpx.AsyncClient, metrics: AnalystMetrics) -> bool:
    """Test analyst pipeline using query processor and data pipeline"""
    start_time = datetime.now().timestamp()
    
    try:
        # Stage 1: Process query using QueryProcessor
        print(f"\nProcessing query: {query}")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        if not query_result or not query_result.requirements:
            metrics.record_code_generation_failure("No requirements generated from query")
            return False
            
        # Stage 2: Get data using Pipeline
        season = query_result.requirements.params.get('season', '2023')
        
        # Determine if we need race results
        needs_race_results = any(word in query.lower() for word in ['win', 'won', 'winner', 'wins', 'victory', 'victories'])
        if needs_race_results:
            endpoint = 'results'  # Override to get race results
        else:
            endpoint = query_result.requirements.endpoint.replace('/api/f1', '')
            if endpoint.startswith('/'):
                endpoint = endpoint[1:]
        
        if not endpoint.endswith('/'):
            endpoint += '/'
            
        # Handle multiple seasons for historical queries
        if isinstance(season, list):
            # For historical queries, we'll need to make multiple requests and combine the results
            all_data = []
            
            for s in season:
                base_url = f"https://api.jolpi.ca/ergast/f1/{s}"
                params = {k: v for k, v in query_result.requirements.params.items() if k != 'season'}
                
                url = f"{base_url}/{endpoint}"
                
                print(f"\nAttempting API request for season {s}...")
                print(f"URL: {url}")
                if params:
                    print(f"Params: {params}")
                
                try:
                    # Add delay between requests to avoid rate limiting
                    await asyncio.sleep(1)
                    response_text = await make_api_request(client, url, params)
                    print(f"API request successful for season {s}")
                    season_data = json.loads(response_text)
                    
                    # Convert season data to DataFrame
                    if 'RaceTable' in season_data['MRData']:
                        season_df = pd.json_normalize(season_data['MRData']['RaceTable']['Races'])
                    elif 'DriverTable' in season_data['MRData']:
                        season_df = pd.json_normalize(season_data['MRData']['DriverTable']['Drivers'])
                    elif 'ConstructorTable' in season_data['MRData']:
                        season_df = pd.json_normalize(season_data['MRData']['ConstructorTable']['Constructors'])
                    else:
                        season_df = pd.json_normalize(season_data['MRData'])
                    
                    # Add season if not present
                    if 'season' not in season_df.columns:
                        season_df['season'] = s
                    
                    all_data.append(season_df)
                except Exception as e:
                    print(f"Failed to fetch data for season {s}: {str(e)}")
                    continue
            
            if not all_data:
                metrics.record_execution_failure("Failed to fetch data for any season")
                return False
            
            # Combine all the data
            df = pd.concat(all_data, ignore_index=True).copy()  # Create a copy to avoid SettingWithCopyWarning
            print(f"\nCombined data shape: {df.shape}")
            print(f"\nCombined data columns: {list(df.columns)}")
            print(f"\nCombined data sample:\n{df.head()}")
            
            # Stage 3: Generate and execute analysis code
            print("\nGenerating analysis code...")
            code_response = generate_code(df, query)
            code_block = extract_code_block(code_response)
            
            if not code_block:
                metrics.record_code_generation_failure("No code block generated")
                return False
                
            metrics.record_code_generation_success()
            
            print("\nExecuting analysis code...")
            success, result, code = execute_code_safely(code_block, df)
            
            if success:
                metrics.record_execution_success()
                print("\nCode executed successfully")
                
                if result.get('figure'):
                    metrics.record_visualization_success()
                    print("Visualization generated successfully")
                else:
                    metrics.record_visualization_failure("No visualization generated")
            else:
                metrics.record_execution_failure(result.get('error', 'Unknown error'))
                print(f"\nExecution error: {result.get('error')}")
                
            processing_time = datetime.now().timestamp() - start_time
            metrics.record_processing_time(processing_time)
            
            return success
        else:
            # Single season query
            base_url = f"https://api.jolpi.ca/ergast/f1/{season}"
            params = {k: v for k, v in query_result.requirements.params.items() if k != 'season'}
            
            url = f"{base_url}/{endpoint}"
            
            print(f"\nAttempting API request...")
            print(f"URL: {url}")
            if params:
                print(f"Params: {params}")
            
            try:
                response_text = await make_api_request(client, url, params)
                print("API request successful")
                data = json.loads(response_text)
                
                print("\nAPI Response Data:")
                print(json.dumps(data, indent=2)[:500] + "...")  # Print first 500 chars of formatted JSON
                
                # Convert JSON data to DataFrame for analysis
                if 'RaceTable' in data['MRData']:
                    df = pd.json_normalize(data['MRData']['RaceTable']['Races'])
                elif 'DriverTable' in data['MRData']:
                    df = pd.json_normalize(data['MRData']['DriverTable']['Drivers'])
                elif 'ConstructorTable' in data['MRData']:
                    df = pd.json_normalize(data['MRData']['ConstructorTable']['Constructors'])
                else:
                    df = pd.json_normalize(data['MRData'])
                
                # Add season if not present
                if 'season' not in df.columns:
                    df['season'] = season
                
                # Stage 3: Generate and execute analysis code
                print("\nGenerating analysis code...")
                code_response = generate_code(df, query)
                code_block = extract_code_block(code_response)
                
                if not code_block:
                    metrics.record_code_generation_failure("No code block generated")
                    return False
                    
                metrics.record_code_generation_success()
                
                print("\nExecuting analysis code...")
                success, result, code = execute_code_safely(code_block, df)
                
                if success:
                    metrics.record_execution_success()
                    print("\nCode executed successfully")
                    
                    if result.get('figure'):
                        metrics.record_visualization_success()
                        print("Visualization generated successfully")
                    else:
                        metrics.record_visualization_failure("No visualization generated")
                else:
                    metrics.record_execution_failure(result.get('error', 'Unknown error'))
                    print(f"\nExecution error: {result.get('error')}")
                    
                processing_time = datetime.now().timestamp() - start_time
                metrics.record_processing_time(processing_time)
                
                return success
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {str(e)}")
                metrics.record_execution_failure(f"JSON parsing failed: {str(e)}")
                return False
            except Exception as e:
                print(f"API request failed: {str(e)}")
                metrics.record_execution_failure(f"API request failed: {str(e)}")
                return False
            
            if data.empty:
                metrics.record_code_generation_failure("No data returned from API")
                return False
            
        # Stage 3: Generate and execute analysis code
        print("\nGenerating analysis code...")
        code_response = generate_code(data, query)
        code_block = extract_code_block(code_response)
        
        if not code_block:
            metrics.record_code_generation_failure("No code block generated")
            return False
            
        metrics.record_code_generation_success()
        
        print("\nExecuting analysis code...")
        success, result, code = execute_code_safely(code_block, data)
        
        if success:
            metrics.record_execution_success()
            print("\nCode executed successfully")
            
            if result.get('figure'):
                metrics.record_visualization_success()
                print("Visualization generated successfully")
            else:
                metrics.record_visualization_failure("No visualization generated")
        else:
            metrics.record_execution_failure(result.get('error', 'Unknown error'))
            print(f"\nExecution error: {result.get('error')}")
            
        processing_time = datetime.now().timestamp() - start_time
        metrics.record_processing_time(processing_time)
        
        return success
        
    except Exception as e:
        error_msg = f"Pipeline Error: {str(e)}\n{traceback.format_exc()}"
        metrics.record_execution_failure(error_msg)
        print(f"Full error for query '{query}': {error_msg}")
        return False

async def run_analyst_tests():
    """Run tests for analyst module using different query categories"""
    metrics = AnalystMetrics()
    
    # Select test queries from different categories
    test_queries = []
    
    # Basic Stats (first 1)
    test_queries.extend(TestQueries.BASIC_STATS.queries[:1])
    
    # Driver Comparisons (first 1)
    test_queries.extend(TestQueries.DRIVER_COMPARISONS.queries[:1])
    
    # Historical Trends (first 1)
    test_queries.extend(TestQueries.HISTORICAL_TRENDS.queries[:1])
    
    print("\nRunning analyst tests with selected queries...")
    print(f"Number of test queries: {len(test_queries)}")
    print("\nQueries to test:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    # Configure client with longer timeout and retries
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    timeout = httpx.Timeout(60.0, connect=30.0)
    transport = httpx.AsyncHTTPTransport(retries=3)
    
    async with httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        transport=transport,
        follow_redirects=True
    ) as client:
        # Process test cases one at a time for better error tracking
        batch_size = 1  # Process one query at a time
        for i in range(0, len(test_queries), batch_size):
            batch = test_queries[i:i + batch_size]
            print(f"\nProcessing query {i + 1}/{len(test_queries)}")
            try:
                tasks = [
                    test_analyst_pipeline(query, client, metrics)
                    for query in batch
                ]
                await asyncio.gather(*tasks)
                print("-" * 80)
            except Exception as e:
                print(f"Error processing batch: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                continue
    
    metrics.print_summary()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
        
    # Run tests
    asyncio.run(run_analyst_tests()) 