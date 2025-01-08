from dataclasses import dataclass, field
from typing import Dict, Any, List, Union, Optional, Tuple
import os
import json
import asyncio
import time
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .models import DataRequirements, ProcessingResult
from .q2_assistants import Q2Processor, Q2Result

# Load environment variables
load_dotenv()

class QueryProcessor:
    """Maps natural language queries to F1 data requirements"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=api_key)
        # Q2: Initialize Q2 processor
        self.q2_processor = Q2Processor(self.client)
        
    async def process_query(self, query: str, use_q2: bool = True) -> ProcessingResult:
        """
        Enhanced query processing with Q2 system
        Maintains backward compatibility while allowing Q2 processing
        """
        results = []
        
        # Q2: Try Q2 processing if enabled
        if use_q2:
            try:
                start_time = time.time()
                q2_result = await self.q2_processor.process_query(query)
                q2_time = time.time() - start_time
                
                results.append(ProcessingResult(
                    requirements=q2_result.requirements,
                    processing_time=q2_time,
                    source='q2',
                    confidence=q2_result.confidence,
                    trace=q2_result.agent_trace
                ))
            except Exception as e:
                print(f"Q2 processing failed: {str(e)}")
        
        # Always run legacy processing for comparison during phase 1
        try:
            start_time = time.time()
            legacy_requirements = await self._legacy_process_query(query)
            legacy_time = time.time() - start_time
            
            results.append(ProcessingResult(
                requirements=legacy_requirements,
                processing_time=legacy_time,
                source='legacy',
                confidence=0.5  # Default confidence for legacy system
            ))
        except Exception as e:
            print(f"Legacy processing failed: {str(e)}")
        
        # Choose the best result
        if not results:
            raise ValueError("Both processing methods failed")
        
        # Q2: During phase 1, prefer Q2 result if confidence is high enough
        q2_results = [r for r in results if r.source == 'q2']
        if q2_results and q2_results[0].confidence > 0.8:
            return q2_results[0]
        
        # Fallback to fastest result with minimum confidence
        valid_results = [r for r in results if r.confidence >= 0.5]
        if valid_results:
            return min(valid_results, key=lambda x: x.processing_time)
        
        return results[0]  # Return any result if none meet criteria
            
    async def _legacy_process_query(self, query: str) -> DataRequirements:
        """Original processing logic maintained for fallback"""
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
        result = await processor.process_query(query)
        print("\nProcessing Result:")
        print(f"Source: {result.source}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Processing Time: {result.processing_time:.3f}s")
        print(f"Endpoint: {result.requirements.endpoint}")
        print(f"Parameters: {json.dumps(result.requirements.params, indent=2)}")
        if result.trace:
            print("\nProcessing Trace:")
            for trace_line in result.trace:
                print(f"  {trace_line}")

if __name__ == "__main__":
    asyncio.run(main())