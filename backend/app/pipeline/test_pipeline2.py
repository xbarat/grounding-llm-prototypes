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
    # Test queries from query_set.txt
    test_queries = [
        "How has Max Verstappen's rank changed across the last 10 seasons?",
        "How does Lewis Hamilton compare to Charles Leclerc in terms of wins, podiums, and points over the last 5 seasons?",
        "What is Fernando Alonso's performance (wins, fastest laps, podiums) on Circuit Silverstone over the past seasons?",
        "What were Sergio Pérez's key stats (wins, poles, fastest laps) for each season?",
        "What is Carlos Sainz Jr.'s average qualifying position across all races in a given season?",
        "How does Lando Norris perform in wet vs. dry conditions (wins, DNFs, lap times)?",
        "How does George Russell compare to his teammate in points, podiums, and wins for the last 3 seasons?",
        "How has Oscar Piastri performed in races with safety car interventions (positions gained/lost)?",
        "What is Valtteri Bottas's average lap time consistency across all races in a season?",
        "How often does Charles Leclerc finish in the top 5 after starting outside the top 10?",
        "How has Lewis Hamilton's rank changed across the last 10 seasons?",
        "How does Max Verstappen compare to Fernando Alonso in terms of wins, podiums, and points over the last 5 seasons?",
        "What is Lando Norris's performance (wins, fastest laps, podiums) on Circuit Monaco over the past seasons?",
        "What were George Russell's key stats (wins, poles, fastest laps) for each season?",
        "What is Oscar Piastri's average qualifying position across all races in a given season?",
        "How does Valtteri Bottas perform in wet vs. dry conditions (wins, DNFs, lap times)?",
        "How does Sergio Pérez compare to his teammate in points, podiums, and wins for the last 3 seasons?",
        "How has Carlos Sainz Jr. performed in races with safety car interventions (positions gained/lost)?",
        "What is Charles Leclerc's average lap time consistency across all races in a season?",
        "How often does Fernando Alonso finish in the top 5 after starting outside the top 10?"
    ]
    
    print("Starting test of all queries...")
    print(f"Total queries to test: {len(test_queries)}")
    print("-" * 80)
    
    # Run tests with a counter
    for i, query in enumerate(test_queries, 1):
        print(f"\nTesting query {i}/{len(test_queries)}")
        print("-" * 40)
        asyncio.run(test_integrated_pipeline(query))
        print("-" * 80) 