import asyncio
import sys
from pathlib import Path
import pandas as pd

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data2 import DataPipeline, DataTransformer
from app.query.processor import QueryProcessor, DataRequirements

async def test_integrated_pipeline(query: str):
    """Test the complete pipeline from natural language to data"""
    
    print("\nTesting integrated pipeline...")
    print(f"Query: {query}")
    
    # Step 1: Process the natural language query
    print("\nStep 1: Processing query...")
    processor = QueryProcessor()
    requirements = await processor.process_query(query)
    print(f"Generated requirements: {requirements}")
    
    # Step 2: Use the requirements to fetch and process data
    print("\nStep 2: Fetching and processing data...")
    pipeline = DataPipeline()
    response = await pipeline.process(requirements)
    
    if response.success and response.data is not None:
        df = response.data["results"]
        
        print("\nData Overview:")
        print("--------------")
        print(f"Total rows: {len(df)}")
        print(f"Columns: {', '.join(df.columns)}")
        
        if requirements.endpoint == "/api/f1/qualifying":
            # Handle qualifying data
            transformer = DataTransformer()
            normalized_df = transformer.normalize_qualifying(df)
            
            print("\nQualifying Results:")
            print("--------------")
            print("Position | Driver | Constructor | Q1 | Q2 | Q3")
            print("-" * 60)
            
            for _, row in normalized_df.sort_values('position').iterrows():
                q1_time = row['Q1'] if pd.notna(row['Q1']) else '-'
                q2_time = row['Q2'] if pd.notna(row['Q2']) else '-'
                q3_time = row['Q3'] if pd.notna(row['Q3']) else '-'
                
                print(f"{row['position']:^8} | {row['driver']:<15} | {row['constructor']:<15} | {q1_time:<8} | {q2_time:<8} | {q3_time:<8}")
                
            # Show fastest times
            print("\nFastest Times:")
            print("--------------")
            for session in ['Q1', 'Q2', 'Q3']:
                if f'{session}_seconds' in normalized_df.columns:
                    fastest_time = normalized_df[normalized_df[f'{session}_seconds'].notna()][f'{session}_seconds'].min()
                    if pd.notna(fastest_time):
                        fastest_driver = normalized_df[normalized_df[f'{session}_seconds'] == fastest_time]['driver'].iloc[0]
                        print(f"{session}: {fastest_driver} - {normalized_df[normalized_df[f'{session}_seconds'] == fastest_time][session].iloc[0]}")
        
        else:
            # Handle race/driver data
            print("\nResults:")
            print("--------------")
            print(df.head())
            
            if 'driver' in df.columns:
                print("\nDriver Statistics:")
                print("------------------")
                for driver in sorted(df['driver'].unique()):
                    driver_df = df[df['driver'] == driver]
                    stats = DataTransformer.calculate_driver_stats(driver_df)
                    print(f"\n{driver}:")
                    for stat, value in sorted(stats.items()):
                        if isinstance(value, float):
                            print(f"  {stat}: {value:.2f}")
                        else:
                            print(f"  {stat}: {value}")
                    
                    if 'season' in df.columns:
                        print("\n  Season breakdown:")
                        for season in sorted(driver_df['season'].unique()):
                            season_df = driver_df[driver_df['season'] == season]
                            season_stats = DataTransformer.calculate_driver_stats(season_df)
                            print(f"    {season}:")
                            print(f"      Wins: {season_stats['wins']}")
                            print(f"      Podiums: {season_stats['podiums']}")
                            print(f"      Points: {season_stats['points']}")
                            print(f"      Avg Position: {season_stats['avg_position']:.2f}")
    else:
        print("\nError occurred:")
        print(response.error)

if __name__ == "__main__":
    # Test queries
    test_queries = [
        "How has Charles Leclerc performed in qualifying at Monaco in 2023?",
        "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?"
    ]
    
    # Run tests
    for query in test_queries:
        asyncio.run(test_integrated_pipeline(query)) 