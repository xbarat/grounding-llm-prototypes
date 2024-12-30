import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = str(Path(__file__).parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.pipeline.data import DataPipeline
from app.query.processor import DataRequirements

async def test_comparison_query():
    # Create test requirements from our successful GPT-4O Mini response
    test_requirements = DataRequirements(
        endpoint="/api/f1/drivers",
        params={
            "season": ["2019", "2020", "2021", "2022", "2023"],
            "driver": ["lewis_hamilton", "charles_leclerc"]
        }
    )
    
    # Initialize pipeline
    pipeline = DataPipeline()
    
    print("\nTesting driver comparison query...")
    print(f"Requirements: {test_requirements}")
    
    # Process the requirements
    result = await pipeline.process(test_requirements)
    
    # Print results
    if result.success:
        print("\nSuccess!")
        print("Data received:", str(result.data)[:500] + "...")  # First 500 chars
    else:
        print("\nError occurred:")
        print(result.error)

if __name__ == "__main__":
    asyncio.run(test_comparison_query()) 