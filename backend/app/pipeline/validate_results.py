import asyncio
import httpx
import pandas as pd
from test_pipeline2 import test_integrated_pipeline
from data_validator import DataFrameValidator
from typing import Dict, Any, Optional

async def validate_test_queries():
    # Original test queries from test_pipeline2.py
    test_queries = [
        "How has Max Verstappen performed in the 2023 season?",
        "What are Lewis Hamilton's stats for 2023?",
        "What was Charles Leclerc's qualifying position in Monaco 2023?",
        "Show me Oscar Piastri's qualifying results for 2023",
        "How many podiums did Fernando Alonso get in 2023?",
        "What's Lando Norris's average finishing position in 2023?",
        "How did George Russell perform at Silverstone in 2023?",
        "Show me Carlos Sainz's results at Monza 2023"
    ]
    
    validator = DataFrameValidator()
    validation_results = {}
    
    async with httpx.AsyncClient() as client:
        for i, query in enumerate(test_queries, 1):
            print(f"\nValidating query {i}/{len(test_queries)}")
            print(f"Query: {query}")
            
            # Run the pipeline and capture the output
            pipeline_output = await test_integrated_pipeline(query, client)
            
            # Extract DataFrame from pipeline output
            df = None
            if isinstance(pipeline_output, tuple):
                # The first element should be the raw DataFrame
                df = pipeline_output[0]
            elif isinstance(pipeline_output, pd.DataFrame):
                df = pipeline_output
            
            if df is None:
                df = pd.DataFrame()
            
            # Print DataFrame info for debugging
            if not df.empty:
                print("\nDataFrame Info:")
                print(f"Shape: {df.shape}")
                print(f"Columns: {df.columns.tolist()}")
                print("\nFirst few rows:")
                print(df.head())
            
            # Determine query type
            query_type = 'qualifying' if 'qualifying' in query.lower() else 'driver_stats'
            
            # Validate DataFrame
            is_valid, metrics = validator.validate_df(df, query_type)
            validation_results[f"Query {i}"] = (is_valid, metrics)
    
    # Log summary
    validator.log_validation_summary(validation_results)
    return validation_results

if __name__ == "__main__":
    asyncio.run(validate_test_queries()) 