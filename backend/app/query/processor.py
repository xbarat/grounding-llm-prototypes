from dataclasses import dataclass
from typing import Dict, Any
import os
import json
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables from .env file
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

Format:
{{
    "endpoint": "/api/f1/...",
    "params": {{
        "param1": "value1",
        "param2": "value2"
    }}
}}

Use snake_case for parameter values. Return only the JSON."""
                }],
                max_tokens=1000
            )
            
            # Extract and clean the content from the response
            raw_content = str(response.content[0])
            content = raw_content.split("text='")[1].split("', type=")[0]
            
            # Clean up the JSON string
            content = content.encode().decode('unicode_escape')
            
            # Parse the JSON
            parsed = json.loads(content)
            
            return DataRequirements(
                endpoint=parsed["endpoint"],
                params=parsed["params"]
            )
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            print("Failed content:", content)
            return DataRequirements(
                endpoint="/api/f1/races",
                params={}
            )

# Example usage
async def main():
    processor = QueryProcessor()
    
    # Test different types of queries
    queries = [
        "What are the results of the 2024 Australian Grand Prix?",
        "Show me Max Verstappen's qualifying results in Monaco 2023",
        "Compare pit stop times between Red Bull and Ferrari in the last race"
    ]
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        requirements = await processor.process_query(query)
        print("Requirements:", requirements)

if __name__ == "__main__":
    asyncio.run(main())