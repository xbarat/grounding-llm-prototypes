"""Full integration tests for F1 data pipeline with actual API endpoints"""

import asyncio
import sys
from pathlib import Path
import pandas as pd
import pytest
import httpx
from datetime import datetime
from typing import Dict, Any, List
import xml.etree.ElementTree as ET
import traceback
import os
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent)
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

# Load environment variables
load_dotenv()

class TestMetrics:
    """Tracks test metrics and performance"""
    def __init__(self):
        self.query_success = 0
        self.query_failure = 0
        self.api_success = 0
        self.api_failure = 0
        self.data_validation_success = 0
        self.data_validation_failure = 0
        self.visualization_success = 0
        self.visualization_failure = 0
        self.processing_times: List[float] = []
        self.errors: List[str] = []
        
    def record_query_success(self):
        self.query_success += 1
        
    def record_query_failure(self, error: str):
        self.query_failure += 1
        self.errors.append(f"Query Error: {error}")
        
    def record_api_success(self):
        self.api_success += 1
        
    def record_api_failure(self, error: str):
        self.api_failure += 1
        self.errors.append(f"API Error: {error}")
        
    def record_validation_success(self):
        self.data_validation_success += 1
        
    def record_validation_failure(self, error: str):
        self.data_validation_failure += 1
        self.errors.append(f"Validation Error: {error}")
        
    def record_visualization_success(self):
        self.visualization_success += 1
        
    def record_visualization_failure(self, error: str):
        self.visualization_failure += 1
        self.errors.append(f"Visualization Error: {error}")
        
    def record_processing_time(self, time: float):
        self.processing_times.append(time)
        
    def print_summary(self):
        total_queries = self.query_success + self.query_failure
        total_api = self.api_success + self.api_failure
        total_validation = self.data_validation_success + self.data_validation_failure
        total_viz = self.visualization_success + self.visualization_failure
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        print("\n=== Test Results Summary ===")
        print(f"\nQuery Processing:")
        print(f"  Success: {self.query_success}/{total_queries} ({(self.query_success/total_queries*100 if total_queries else 0):.1f}%)")
        print(f"  Failure: {self.query_failure}/{total_queries} ({(self.query_failure/total_queries*100 if total_queries else 0):.1f}%)")
        
        print(f"\nAPI Calls:")
        print(f"  Success: {self.api_success}/{total_api} ({(self.api_success/total_api*100 if total_api else 0):.1f}%)")
        print(f"  Failure: {self.api_failure}/{total_api} ({(self.api_failure/total_api*100 if total_api else 0):.1f}%)")
        
        print(f"\nData Validation:")
        print(f"  Success: {self.data_validation_success}/{total_validation} ({(self.data_validation_success/total_validation*100 if total_validation else 0):.1f}%)")
        print(f"  Failure: {self.data_validation_failure}/{total_validation} ({(self.data_validation_failure/total_validation*100 if total_validation else 0):.1f}%)")
        
        print(f"\nVisualization Generation:")
        print(f"  Success: {self.visualization_success}/{total_viz} ({(self.visualization_success/total_viz*100 if total_viz else 0):.1f}%)")
        print(f"  Failure: {self.visualization_failure}/{total_viz} ({(self.visualization_failure/total_viz*100 if total_viz else 0):.1f}%)")
        
        print(f"\nPerformance:")
        print(f"  Average Processing Time: {avg_time:.2f} seconds")
        print(f"  Total Tests Run: {total_queries}")
        
        if self.errors:
            print("\nErrors Encountered:")
            for error in self.errors:
                print(f"  - {error}")

def xml_to_dataframe(xml_data: str, endpoint: str) -> pd.DataFrame:
    """Convert XML response to pandas DataFrame"""
    root = ET.fromstring(xml_data)
    
    # Define namespace mapping
    ns = {'ns': 'http://ergast.com/mrd/1.5'}
    
    data = []
    if 'drivers' in endpoint:
        # Extract driver data
        drivers = root.findall('.//ns:DriverTable//ns:Driver', ns)
        for driver in drivers:
            data.append({
                'driverId': driver.get('driverId'),
                'code': driver.find('ns:Code', ns).text if driver.find('ns:Code', ns) is not None else '',
                'givenName': driver.find('ns:GivenName', ns).text,
                'familyName': driver.find('ns:FamilyName', ns).text,
                'nationality': driver.find('ns:Nationality', ns).text
            })
    elif 'qualifying' in endpoint:
        # Extract qualifying data
        races = root.findall('.//ns:Race', ns)
        for race in races:
            qualifying_results = race.findall('.//ns:QualifyingResult', ns)
            for quali in qualifying_results:
                driver = quali.find('.//ns:Driver', ns)
                data.append({
                    'round': race.get('round'),
                    'raceName': race.find('ns:RaceName', ns).text,
                    'position': quali.get('position'),
                    'driverId': driver.get('driverId'),
                    'q1': quali.find('ns:Q1', ns).text if quali.find('ns:Q1', ns) is not None else '',
                    'q2': quali.find('ns:Q2', ns).text if quali.find('ns:Q2', ns) is not None else '',
                    'q3': quali.find('ns:Q3', ns).text if quali.find('ns:Q3', ns) is not None else ''
                })
    elif 'results' in endpoint:
        # Extract race results data
        races = root.findall('.//ns:Race', ns)
        for race in races:
            results = race.findall('.//ns:Result', ns)
            for result in results:
                driver = result.find('.//ns:Driver', ns)
                data.append({
                    'round': race.get('round'),
                    'raceName': race.find('ns:RaceName', ns).text,
                    'position': result.get('position'),
                    'points': result.get('points'),
                    'driverId': driver.get('driverId'),
                    'laps': result.find('ns:Laps', ns).text,
                    'status': result.find('ns:Status', ns).text
                })
    elif 'constructors' in endpoint:
        # Extract constructor data
        constructors = root.findall('.//ns:ConstructorTable//ns:Constructor', ns)
        for constructor in constructors:
            data.append({
                'constructorId': constructor.get('constructorId'),
                'name': constructor.find('ns:Name', ns).text,
                'nationality': constructor.find('ns:Nationality', ns).text
            })
    elif 'circuits' in endpoint:
        # Extract circuit data
        circuits = root.findall('.//ns:CircuitTable//ns:Circuit', ns)
        for circuit in circuits:
            location = circuit.find('.//ns:Location', ns)
            data.append({
                'circuitId': circuit.get('circuitId'),
                'name': circuit.find('ns:CircuitName', ns).text,
                'location': location.find('ns:Locality', ns).text if location is not None else '',
                'country': location.find('ns:Country', ns).text if location is not None else ''
            })
    elif 'driverStandings' in endpoint:
        # Extract driver standings data
        standings = root.findall('.//ns:StandingsTable//ns:DriverStanding', ns)
        for standing in standings:
            driver = standing.find('.//ns:Driver', ns)
            constructor = standing.find('.//ns:Constructor', ns)
            data.append({
                'position': standing.get('position'),
                'points': standing.get('points'),
                'wins': standing.get('wins'),
                'driverId': driver.get('driverId'),
                'constructorId': constructor.get('constructorId') if constructor is not None else ''
            })
    
    return pd.DataFrame(data)

class TestDataValidator:
    """Validates the structure and content of API responses"""
    
    @staticmethod
    def validate_driver_data(df: pd.DataFrame) -> bool:
        """Validate driver endpoint response"""
        required_columns = {'driverId', 'givenName', 'familyName', 'nationality'}
        return all(col in df.columns for col in required_columns)
    
    @staticmethod
    def validate_qualifying_data(df: pd.DataFrame) -> bool:
        """Validate qualifying endpoint response"""
        required_columns = {'position', 'driverId', 'q1'}
        return all(col in df.columns for col in required_columns)
    
    @staticmethod
    def validate_race_data(df: pd.DataFrame) -> bool:
        """Validate race endpoint response"""
        required_columns = {'position', 'points', 'status', 'laps'}
        return all(col in df.columns for col in required_columns)

async def test_full_pipeline(query: str, client: httpx.AsyncClient, metrics: TestMetrics) -> bool:
    """Test the full pipeline from query to data retrieval and visualization"""
    start_time = datetime.now().timestamp()
    
    try:
        # Step 1: Process the query using QueryProcessor
        print(f"\nProcessing query: {query}")
        processor = QueryProcessor()
        query_result = await processor.process_query(query)
        
        if not query_result or not query_result.requirements:
            metrics.record_query_failure("No requirements generated")
            return False
            
        metrics.record_query_success()
        print(f"\nGenerated requirements:")
        print(f"Endpoint: {query_result.requirements.endpoint}")
        print(f"Parameters: {query_result.requirements.params}")
        
        # Step 2: Convert requirements to API call
        season = query_result.requirements.params.get('season', '2023')
        base_url = f"https://ergast.com/api/f1/{season}"
        
        # Remove season from params as it's now in the URL
        params = {k: v for k, v in query_result.requirements.params.items() if k != 'season'}
        
        # Extract endpoint from requirements
        endpoint = query_result.requirements.endpoint.replace('/api/f1', '')
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
            
        url = f"{base_url}/{endpoint}"
        
        print(f"\nCalling API: {url}")
        if params:
            print(f"With params: {params}")
        
        # Step 3: Make the API call
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        # Step 4: Process and validate the response
        df = xml_to_dataframe(response.text, endpoint)
        
        if df.empty:
            metrics.record_validation_failure("No data returned")
            return False
        
        # Validate the data structure
        validator = TestDataValidator()
        if 'drivers' in endpoint:
            is_valid = validator.validate_driver_data(df)
        elif 'qualifying' in endpoint:
            is_valid = validator.validate_qualifying_data(df)
        elif 'results' in endpoint:
            is_valid = validator.validate_race_data(df)
        else:
            is_valid = True
        
        if is_valid:
            metrics.record_validation_success()
        else:
            metrics.record_validation_failure("Invalid data structure")
            
        metrics.record_api_success()
        
        # Step 5: Prepare data for visualization
        print("\nPreparing data for visualization...")
        
        # Convert numeric columns
        numeric_columns = ['position', 'points', 'round', 'season']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Add metadata to help with visualization
        df['query_type'] = query_result.source
        if 'season' not in df.columns:
            df['season'] = season
            
        # Print data info for debugging
        print("\nData Info:")
        print(df.info())
        print("\nData Sample:")
        print(df.head())
        
        # Step 6: Generate visualization
        print("\nGenerating visualization...")
        code_response = generate_code(df, query)
        code_block = extract_code_block(code_response)
        
        if not code_block:
            metrics.record_visualization_failure("No code block generated")
            return False
            
        success, result, code = execute_code_safely(code_block, df)
        
        if success:
            metrics.record_visualization_success()
            print("\nVisualization generated successfully")
            print(f"Code executed:\n{code}")
            if result.get('figure'):
                print("Figure generated and encoded in base64")
                # Save the visualization if needed
                # with open(f"viz_{endpoint}_{season}.png", "wb") as f:
                #     f.write(base64.b64decode(result['figure']))
        else:
            metrics.record_visualization_failure(result.get('error', 'Unknown error'))
            print(f"\nVisualization error: {result.get('error')}")
            
        processing_time = datetime.now().timestamp() - start_time
        metrics.record_processing_time(processing_time)
        
        return True
        
    except Exception as e:
        metrics.record_api_failure(f"Pipeline Error: {str(e)}")
        print(f"Full error for query '{query}': {traceback.format_exc()}")
        return False

async def run_full_test():
    """Run comprehensive tests through the entire pipeline"""
    metrics = TestMetrics()
    
    # Test cases with natural language queries
    test_cases = [
        "Show me Max Verstappen's points progression throughout the 2023 season",
        "Compare qualifying times between Hamilton and Verstappen in 2023",
        "Plot the number of podiums for each constructor in 2023",
        "Show me the distribution of pit stop times in the 2023 Monaco GP",
        "Create a bar chart of wins by driver in 2023",
        "Visualize the points gap between Red Bull drivers over the season",
        "Plot the qualifying improvements of McLaren through 2023",
        "Show me the average finishing positions for all drivers in 2023",
        "Create a heatmap of fastest lap times by circuit in 2023",
        "Visualize the correlation between grid position and race finish position"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Process test cases in parallel batches
        batch_size = 2  # Smaller batch size due to OpenAI API rate limits
        for i in range(0, len(test_cases), batch_size):
            batch = test_cases[i:i + batch_size]
            tasks = [
                test_full_pipeline(query, client, metrics)
                for query in batch
            ]
            await asyncio.gather(*tasks)
    
    metrics.print_summary()

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    asyncio.run(run_full_test()) 