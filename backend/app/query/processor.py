from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import json
from anthropic import AsyncAnthropic

@dataclass
class DataRequirements:
    """Requirements for fetching F1 data"""
    endpoint: str  # The F1 API endpoint to query
    params: Dict[str, Any]  # Parameters for the API call

class QueryProcessor:
    """Process natural language queries into F1 data requirements using Claude"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Available F1 endpoints and their purposes
        self.endpoints = {
            "/api/f1/races": "Race results and basic race information",
            "/api/f1/qualifying": "Qualifying session results and timing data",
            "/api/f1/drivers": "Driver information and statistics",
            "/api/f1/constructors": "Constructor (team) information and statistics",
            "/api/f1/laps": "Detailed lap timing data",
            "/api/f1/pitstops": "Pit stop timing and strategy data"
        }

    async def process_query(self, query: str) -> DataRequirements:
        """
        Process a user query to determine what F1 data needs to be fetched.
        
        Example queries:
        - "Show me Max Verstappen's race positions in 2023"
        - "Compare pit stop times between Red Bull and Ferrari"
        - "What was the qualifying result in Monaco 2023?"
        """
        # Build the prompt
        prompt = self._build_prompt(query)
        
        try:
            # Get response from Claude
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse the response
            content = str(response.content[0])
            parsed = json.loads(content)
            
            return DataRequirements(
                endpoint=parsed["endpoint"],
                params=parsed["params"]
            )
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            # Fallback to default if parsing fails
            return DataRequirements(
                endpoint="/api/f1/races",
                params={}
            )

    def _build_prompt(self, query: str) -> str:
        """Build a prompt for Claude to extract data requirements from the query"""
        endpoints_info = "\n".join(f"- {endpoint}: {desc}" for endpoint, desc in self.endpoints.items())
        
        return f"""You are an F1 data analyst. Given a user query, determine which F1 API endpoint to use and what parameters to include.

Available F1 API endpoints:
{endpoints_info}

Common parameter types:
- year: The season year (e.g., 2023)
- round: The race round number in the season
- driver: Driver identifier (e.g., "max_verstappen", "hamilton")
- constructor: Team identifier (e.g., "red_bull", "ferrari")
- circuit: Circuit identifier (e.g., "monza", "monaco")

User query: {query}

Analyze the query and respond with a JSON object containing:
1. The most appropriate endpoint to fetch the required data
2. The parameters needed to filter/fetch the specific data

Format your response as a JSON object like this:
{{
    "endpoint": string,  // One of the available endpoints
    "params": {{         // Parameters needed for the query
        "param1": value1,
        "param2": value2
    }}
}}

Remember:
1. Choose the most appropriate endpoint from the available options
2. Include all relevant parameters needed to fetch the specific data
3. Use snake_case for parameter values (e.g., "max_verstappen" not "Max Verstappen")
4. Return only the JSON object, no other text"""

    def _clean_param_value(self, value: str) -> str:
        """Clean and format parameter values for consistency"""
        return value.lower().replace(" ", "_")