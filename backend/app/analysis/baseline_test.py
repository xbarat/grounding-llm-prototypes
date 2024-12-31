"""Baseline test for Claude's analysis capabilities"""
import asyncio
import pandas as pd
import httpx
from ..pipeline.data2 import DataPipeline, DataRequirements
from ..pipeline.mappings import get_round_number, normalize_circuit_id

ZERO_SHOT_PROMPT = """You are an expert F1 data analyst. Given a DataFrame and a query, generate Python code to analyze the data and create appropriate visualizations.
Use matplotlib and seaborn for visualizations. Make the plots clear and professional.

DataFrame Description:
{df_info}

User Query: {query}

Generate Python code to analyze this data and create visualizations. The code should be complete and ready to run.
Only output the code, no explanations needed."""

TEST_QUERIES = [
    {
        "query": "How has Max Verstappen's performance evolved over the 2023 season?",
        "requirements": DataRequirements(
            endpoint="/api/f1/drivers",
            params={"season": "2023", "driver": "max_verstappen"}
        )
    },
    {
        "query": "Compare qualifying performances of Charles Leclerc and Carlos Sainz at Monaco 2023",
        "requirements": DataRequirements(
            endpoint="/api/f1/qualifying",
            params={
                "season": "2023", 
                "round": str(get_round_number(normalize_circuit_id("monaco"), "2023") or 6),
                "circuit": "monaco"
            }
        )
    },
    {
        "query": "Show the points progression of Lewis Hamilton throughout 2023",
        "requirements": DataRequirements(
            endpoint="/api/f1/drivers",
            params={"season": "2023", "driver": "lewis_hamilton"}
        )
    },
    {
        "query": "Compare the qualifying gaps between teammates at Red Bull (Max vs Sergio) in 2023",
        "requirements": DataRequirements(
            endpoint="/api/f1/qualifying",
            params={"season": "2023", "round": "1"}  # Start with first race
        )
    }
]

async def get_data_for_query(pipeline: DataPipeline, requirements: DataRequirements) -> pd.DataFrame:
    """Fetch data for a query"""
    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        pipeline.client = client
        response = await pipeline.process(requirements)
        if response.success and response.data is not None:
            return response.data["results"]
    return pd.DataFrame()

def get_dataframe_info(df: pd.DataFrame) -> str:
    """Get DataFrame information as a string"""
    info = []
    info.append("Columns:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample = str(df[col].iloc[0]) if not df.empty else "N/A"
        info.append(f"- {col} ({dtype}), example: {sample}")
    
    info.append(f"\nShape: {df.shape}")
    info.append(f"Index: {df.index.dtype}")
    
    # Add some basic statistics
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if not numeric_cols.empty:
        info.append("\nNumeric Column Statistics:")
        for col in numeric_cols:
            stats = df[col].describe()
            info.append(f"\n{col}:")
            info.append(f"  min: {stats['min']}")
            info.append(f"  max: {stats['max']}")
            info.append(f"  mean: {stats['mean']:.2f}")
    
    return "\n".join(info)

async def run_baseline_tests():
    """Run baseline tests for Claude's analysis capabilities"""
    pipeline = DataPipeline()
    
    print("Starting baseline tests...")
    print("=" * 80)
    
    for test in TEST_QUERIES:
        print(f"\nTesting Query: {test['query']}")
        print("-" * 80)
        
        # Get data
        df = await get_data_for_query(pipeline, test["requirements"])
        if df.empty:
            print("Failed to get data")
            continue
            
        # Generate prompt
        df_info = get_dataframe_info(df)
        prompt = ZERO_SHOT_PROMPT.format(
            df_info=df_info,
            query=test["query"]
        )
        
        print("\nDataFrame Info:")
        print(df_info)
        
        print("\nGenerated Prompt:")
        print(prompt)
        
        print("\nNow you can copy this prompt to Claude to test its code generation")
        print("=" * 80)
        
        # Save data for testing
        output_file = f"test_data_{test['requirements'].endpoint.replace('/', '_')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSaved test data to: {output_file}")

if __name__ == "__main__":
    asyncio.run(run_baseline_tests()) 