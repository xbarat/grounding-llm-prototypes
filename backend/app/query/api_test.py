import http.client
import json
from typing import Dict, Any, Optional
import time
import pandas as pd
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Setup logging directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_generated_code(query: str, code: Optional[str], success: bool):
    """
    Log generated code to a file
    
    Args:
        query: The original query
        code: The generated code (or error message if None)
        success: Whether the code generation was successful
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = "success" if success else "failed"
    filename = f"generated_code_{timestamp}_{status}.py"
    
    with open(os.path.join(LOG_DIR, filename), 'w') as f:
        f.write(f"# Query: {query}\n")
        f.write(f"# Generated at: {datetime.now().isoformat()}\n")
        f.write(f"# Status: {status}\n\n")
        f.write(code if code is not None else "# No code was generated")
    
    print(f"\nLogged generated code to: {filename}")

# Add the parent directory to sys.path to import from analyst
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyst.generate import generate_code, execute_code_safely, extract_code_block

def fetch_f1_data(endpoint: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch data from Ergast F1 API
    Returns None if the request fails
    """
    conn = http.client.HTTPConnection("ergast.com")
    headers = {
        'User-Agent': 'F1-Analytics/1.0',
        'Accept': 'application/json'
    }
    
    try:
        print(f"\nFetching data from: {endpoint}")
        conn.request("GET", endpoint, '', headers)
        res = conn.getresponse()
        
        if res.status == 200:
            data = res.read()
            return json.loads(data.decode("utf-8"))
        else:
            print(f"Error: Status code {res.status}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None
    finally:
        conn.close()

def process_f1_data(raw_data: Dict[Any, Any]) -> pd.DataFrame:
    """
    Convert raw F1 API data into a pandas DataFrame
    """
    if not raw_data or 'MRData' not in raw_data:
        return pd.DataFrame()

    # Extract the main data table
    data = raw_data['MRData']
    
    # Identify the main table (RaceTable, DriverTable, etc.)
    table_key = next((k for k in data.keys() if k.endswith('Table')), None)
    if not table_key:
        return pd.DataFrame()

    table_data = data[table_key]
    
    # Handle different table types
    if 'Races' in table_data:
        # Flatten race data
        races_data = []
        for race in table_data['Races']:
            race_info = {
                'season': race['season'],
                'round': race['round'],
                'raceName': race['raceName'],
                'date': race.get('date', ''),
                'circuitId': race['Circuit']['circuitId'],
                'circuitName': race['Circuit']['circuitName']
            }
            
            # Add results if available
            if 'Results' in race:
                for result in race['Results']:
                    result_info = race_info.copy()
                    result_info.update({
                        'driverId': result['Driver']['driverId'],
                        'driverName': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                        'constructorId': result['Constructor']['constructorId'],
                        'position': result.get('position', ''),
                        'points': result.get('points', '0')
                    })
                    races_data.append(result_info)
            else:
                races_data.append(race_info)
        return pd.DataFrame(races_data)
        
    elif 'Drivers' in table_data:
        # Process driver data
        drivers_data = [{
            'driverId': driver['driverId'],
            'driverNumber': driver.get('permanentNumber', ''),
            'code': driver.get('code', ''),
            'driverName': f"{driver['givenName']} {driver['familyName']}",
            'nationality': driver.get('nationality', '')
        } for driver in table_data['Drivers']]
        return pd.DataFrame(drivers_data)
        
    elif 'StandingsLists' in table_data:
        # Process standings data
        standings_data = []
        for standing_list in table_data['StandingsLists']:
            if 'ConstructorStandings' in standing_list:
                for standing in standing_list['ConstructorStandings']:
                    standings_data.append({
                        'position': standing['position'],
                        'points': standing['points'],
                        'wins': standing['wins'],
                        'constructorId': standing['Constructor']['constructorId'],
                        'constructorName': standing['Constructor']['name'],
                        'nationality': standing['Constructor']['nationality']
                    })
            elif 'DriverStandings' in standing_list:
                for standing in standing_list['DriverStandings']:
                    standings_data.append({
                        'position': standing['position'],
                        'points': standing['points'],
                        'wins': standing['wins'],
                        'driverId': standing['Driver']['driverId'],
                        'driverName': f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                        'constructorId': standing['Constructors'][0]['constructorId']
                    })
        return pd.DataFrame(standings_data)
    
    return pd.DataFrame()

def analyze_and_visualize(endpoint: str, query: str) -> Dict[str, Any]:
    """
    Fetch F1 data, process it, and generate visualization based on the query
    
    Args:
        endpoint (str): The F1 API endpoint to fetch data from
        query (str): The natural language query to analyze the data
        
    Returns:
        Dict containing success status, visualization, and any error messages
    """
    try:
        # Fetch raw data
        raw_data = fetch_f1_data(endpoint)
        if not raw_data:
            return {
                "success": False,
                "error": "Failed to fetch data from F1 API"
            }
            
        # Process into DataFrame
        df = process_f1_data(raw_data)
        if df.empty:
            return {
                "success": False,
                "error": "No data available for analysis"
            }
            
        print("\nProcessed DataFrame:")
        print(df.head())
        print("\nColumns:", df.columns.tolist())
        
        # Generate visualization code
        generated_code = generate_code(df, query)
        if not generated_code:
            return {
                "success": False,
                "error": "Failed to generate visualization code"
            }
            
        # Extract the actual code from the markdown code block
        code = extract_code_block(generated_code)
        if not code:
            log_generated_code(query, generated_code, False)
            return {
                "success": False,
                "error": "Failed to extract code from generated response"
            }
            
        # Log the extracted code
        log_generated_code(query, code, True)
            
        # Execute the code
        success, result, executed_code = execute_code_safely(code, df)
        if not success:
            return {
                "success": False,
                "error": f"Failed to execute visualization code: {result.get('error', 'Unknown error')}"
            }
            
        return result
        
    except Exception as e:
        if 'code' in locals():
            log_generated_code(query, code, False)
        return {
            "success": False,
            "error": f"Error in analysis pipeline: {str(e)}"
        }

def run_test_queries():
    """
    Test different API endpoints
    """
    # Test cases combining endpoints and queries
    test_cases = [
        {
            "endpoint": "/api/f1/2023/drivers.json",
            "query": "Show the distribution of driver nationalities in 2023"
        },
        {
            "endpoint": "/api/f1/2023/constructorStandings.json",
            "query": "Create a bar chart of constructor points in 2023"
        },
        {
            "endpoint": "/api/f1/2023/drivers/max_verstappen/results/1.json",
            "query": "Show Max Verstappen's race wins in 2023"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nProcessing: {test_case['query']}")
        result = analyze_and_visualize(test_case['endpoint'], test_case['query'])
        
        if result['success']:
            print("✓ Successfully generated visualization")
            if 'output' in result:
                print("Output:", result['output'])
        else:
            print("✗ Error:", result['error'])
            
        # Respect rate limiting
        time.sleep(0.25)

if __name__ == "__main__":
    print("Starting F1 API Tests with Visualization...")
    run_test_queries() 