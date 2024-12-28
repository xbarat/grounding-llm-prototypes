import asyncio
import os
from dotenv import load_dotenv
from app.query.processor import QueryProcessor
from app.pipeline.data import DataPipeline, DataResponse
from app.engine.analysis import AnalysisEngine
from app.query.analysis import AnalysisQuery
import pandas as pd

# Load environment variables
load_dotenv()

async def process_f1_query(query: str):
    """Process an F1 query through the entire pipeline."""
    print("\n" + "=" * 80)
    print(f"Processing query: {query}")
    print("=" * 80 + "\n")

    try:
        # 1. Initialize components
        query_processor = QueryProcessor()  # Uses env var for API key
        data_pipeline = DataPipeline()
        analysis_engine = AnalysisEngine()  # Uses env var for API key

        # 2. Process query
        print("1. Query Processing")
        print("-" * 17)
        data_reqs, _ = await query_processor.process_query(query)
        print(f"Data Requirements: {data_reqs}")

        # 3. Fetch data
        print("\n2. Data Fetching")
        print("-" * 14)
        data_response = await data_pipeline.process(data_reqs)
        if not data_response.success:
            raise Exception(f"Error fetching data: {data_response.error}")
        print("Data fetched successfully")

        # 4. Process data
        print("\n3. Data Processing")
        print("-" * 15)
        if not data_response.data:
            raise Exception("No data returned from the pipeline")
            
        # Convert API response to DataFrame
        if data_reqs.endpoint == '/api/f1/qualifying':
            races = data_response.data['MRData']['RaceTable']['Races']
            if races:
                qualifying_data = []
                for race in races:
                    for quali in race['QualifyingResults']:
                        qualifying_data.append({
                            'driverId': quali['Driver']['driverId'],
                            'position': quali['position'],
                            'q1': quali.get('Q1', ''),
                            'q2': quali.get('Q2', ''),
                            'q3': quali.get('Q3', '')
                        })
                df = pd.DataFrame(qualifying_data)
            else:
                raise Exception("No qualifying data found")
        else:
            raise Exception(f"Endpoint {data_reqs.endpoint} not yet supported for DataFrame conversion")

        print(f"DataFrame Shape: {df.shape}\n")
        print("First few rows:")
        print(df.head())

        # 5. Generate and execute analysis
        print("\n4. Code Generation")
        print("-" * 16)
        analysis_result = await analysis_engine.analyze(df, query)
        
        print("\nGenerated Analysis Code:")
        print("=" * 40)
        print(analysis_result.code)
        print("=" * 40)
        
        if analysis_result.error:
            print(f"\nError during analysis: {analysis_result.error}")
        else:
            print("\nAnalysis Result:")
            print("-" * 15)
            print(analysis_result.result)

    except Exception as e:
        print(f"\nError processing query: {str(e)}")

async def main():
    # Test query
    query = "Compare qualifying times between Verstappen and Hamilton at Monaco 2023"
    await process_f1_query(query)

if __name__ == "__main__":
    asyncio.run(main()) 