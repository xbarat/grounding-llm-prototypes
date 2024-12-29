from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import os
import json
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DataRequirements:
    """Requirements for fetching F1 data"""
    endpoint: str  # The F1 API endpoint to query
    params: Dict[str, Any]  # Parameters for the API call

class QueryProcessor:
    """Maps natural language queries to F1 data requirements"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = AsyncAnthropic(api_key=api_key)

    async def process_query(self, query: str) -> DataRequirements:
        """
        Maps a user query to F1 data requirements.
        Returns which endpoint to query and what parameters to use.
        """
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                messages=[{
                    "role": "user",
                    "content": f"""Given this F1-related query: "{query}"

Return a JSON object specifying:
1. Which F1 API endpoint to use (one of: /api/f1/races, /api/f1/qualifying, /api/f1/drivers, /api/f1/constructors, /api/f1/laps, /api/f1/pitstops)
2. What parameters to include in the API call

Required parameter formats:
- Season/year should be in params as 'season'
- Circuit names should be in snake_case (e.g., 'monaco', 'silverstone')
- Driver IDs should be in snake_case (e.g., 'lewis_hamilton', 'max_verstappen')
- Constructor IDs should be in snake_case (e.g., 'red_bull', 'ferrari')
- Round numbers should be numeric (e.g., '1', '2', '3')

Example:
{
    "endpoint": "/api/f1/qualifying",
    "params": {
        "season": "2023",
        "circuit": "monaco",
        "driver": ["max_verstappen", "lewis_hamilton"]
    }
}

Return only the JSON object, nothing else."""
                }],
                max_tokens=1000
            )
            
            # Extract and clean the content from the response
            content = str(response.content)
            
            # Find the JSON block
            start = content.find('{')
            end = content.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = content[start:end]
            
            # Parse the JSON
            parsed = json.loads(json_str)
            
            return DataRequirements(
                endpoint=parsed["endpoint"],
                params=parsed["params"]
            )
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            # Return qualifying endpoint for comparison queries
            if "compare" in query.lower() and "qualifying" in query.lower():
                return DataRequirements(
                    endpoint="/api/f1/qualifying",
                    params={
                        "season": "2023",
                        "circuit": "monaco",
                        "driver": ["max_verstappen", "lewis_hamilton"]
                    }
                )
            # Default to races endpoint
            return DataRequirements(
                endpoint="/api/f1/races",
                params={}
            )

# Test queries
async def main():
    processor = QueryProcessor()
    
    # Test different types of queries
    queries = [
        "What are the results of the 2024 Australian Grand Prix?",
        "How did Lewis Hamilton perform in qualifying at Monaco 2023?",
        "Show me Red Bull's constructor points for 2023"
    ]
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        requirements = await processor.process_query(query)
        print("Requirements:", requirements)

if __name__ == "__main__":
    asyncio.run(main())