from dataclasses import dataclass
from typing import Dict, Any, List, Union
import os
import json
import asyncio
from openai import AsyncOpenAI
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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=api_key)

    async def process_query(self, query: str) -> DataRequirements:
        """
        Maps a user query to F1 data requirements.
        Returns a DataRequirements object with endpoint and parameters.
        """
        try:
            print("\nSending request to GPT-4O Mini...")
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": """Extract relevant F1-related information from the given query to create a structured JSON object.

The response must adhere to this exact JSON structure:
{
    "endpoint": string,  // One of: /api/f1/races, /api/f1/qualifying, /api/f1/drivers, /api/f1/constructors, /api/f1/laps, /api/f1/pitstops
    "params": {
        "season": string | string[],  // Optional, year like "2023" or array of years
        "circuit": string,            // Optional, snake_case like "monaco"
        "driver": string | string[],  // Optional, snake_case like "max_verstappen"
        "constructor": string,        // Optional, snake_case like "red_bull"
        "round": string               // Optional, numeric like "1"
    }
}

Query: """ + query
                }],
                temperature=0,
                response_format={ "type": "json_object" }
            )
            
            print("\nReceived response from GPT-4O Mini")
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content in response")
                
            print("\nParsing response...")
            parsed = json.loads(content)
            
            # Validate response structure
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a JSON object")
            if "endpoint" not in parsed:
                raise ValueError("Missing 'endpoint' in response")
            if "params" not in parsed:
                raise ValueError("Missing 'params' in response")
            
            # Create DataRequirements object
            requirements = DataRequirements(
                endpoint=parsed["endpoint"],
                params=parsed["params"]
            )
            
            print("\nProcessed requirements:", requirements)
            return requirements
            
        except Exception as e:
            print(f"\nError processing query: {str(e)}")
            # Return a safe default focused on the driver if we can extract it
            default_driver = query.lower().split()[0] if query else "unknown"
            return DataRequirements(
                endpoint="/api/f1/drivers",
                params={"driver": default_driver}
            )

async def main():
    processor = QueryProcessor()
    
    print("\nF1 Query Processor")
    print("------------------")
    print("Type your questions about F1 data and get structured API requirements.")
    print("Example: 'How has Max Verstappen's rank changed across the last 10 seasons?'")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("\nEnter your F1 query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        print(f"\nProcessing query: {query}")
        requirements = await processor.process_query(query)
        print("\nAPI Requirements:")
        print(f"Endpoint: {requirements.endpoint}")
        print(f"Parameters: {json.dumps(requirements.params, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())