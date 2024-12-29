from typing import Dict, Any, Optional
import httpx
import asyncio
from dataclasses import dataclass
from app.query.processor import DataRequirements, QueryProcessor

@dataclass
class DataResponse:
    """Response from the data pipeline"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DataPipeline:
    """Handles data fetching and processing for F1 data"""
    
    def __init__(self, base_url: str = "http://ergast.com/api/f1"):
        self.base_url = base_url.rstrip('/')
        self.valid_endpoints = {
            "/api/f1/races": "Get race results and information",
            "/api/f1/qualifying": "Get qualifying results",
            "/api/f1/drivers": "Get driver information",
            "/api/f1/constructors": "Get constructor information",
            "/api/f1/laps": "Get lap timing data",
            "/api/f1/pitstops": "Get pit stop information"
        }
        
        # Driver ID mapping
        self.driver_ids = {
            "lewis_hamilton": "hamilton",
            "max_verstappen": "max_verstappen",
            "charles_leclerc": "leclerc",
            "sergio_perez": "perez",
            "carlos_sainz": "sainz",
            "george_russell": "russell",
            "lando_norris": "norris",
            "fernando_alonso": "alonso"
        }
        
        # Constructor ID mapping
        self.constructor_ids = {
            "red_bull": "red_bull",
            "mercedes": "mercedes",
            "ferrari": "ferrari",
            "mclaren": "mclaren",
            "aston_martin": "aston_martin",
            "alpine": "alpine",
            "williams": "williams",
            "alphatauri": "alphatauri",
            "alfa": "alfa",
            "haas": "haas"
        }
        
        # Circuit round mapping for 2023
        self.circuit_rounds_2023 = {
            "bahrain": "1",
            "jeddah": "2",
            "albert_park": "3",
            "baku": "4",
            "miami": "5",
            "monaco": "6",
            "barcelona": "7",
            "montreal": "8",
            "spielberg": "9",
            "silverstone": "10",
            "hungaroring": "11",
            "spa": "12",
            "zandvoort": "13",
            "monza": "14",
            "marina_bay": "15",
            "suzuka": "16",
            "losail": "17",
            "austin": "18",
            "mexico_city": "19",
            "interlagos": "20",
            "las_vegas": "21",
            "yas_marina": "22"
        }
        
    async def process(self, requirements: DataRequirements) -> DataResponse:
        """
        Process data requirements and fetch data from the F1 API.
        First validates the requirements, then attempts to fetch the data.
        """
        # Validate endpoint
        if not self._validate_endpoint(requirements.endpoint):
            return DataResponse(
                success=False,
                error=f"Invalid endpoint: {requirements.endpoint}. Valid endpoints are: {list(self.valid_endpoints.keys())}"
            )
            
        try:
            # Build the URL
            url = self._build_url(requirements)
            print(f"Fetching data from: {url}")  # Debug output
            
            # Add JSON format
            url = f"{url}.json"
            
            # Fetch the data
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                return DataResponse(
                    success=True,
                    data=response.json()
                )
                
        except httpx.HTTPError as e:
            return DataResponse(
                success=False,
                error=f"HTTP error occurred: {str(e)}"
            )
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error fetching data: {str(e)}"
            )
    
    def _validate_endpoint(self, endpoint: str) -> bool:
        """Validate if the endpoint is supported"""
        return endpoint in self.valid_endpoints
    
    def _build_url(self, requirements: DataRequirements) -> str:
        """Build the API URL from the requirements"""
        # Start with base URL
        url = self.base_url
        
        # Add season if present
        if "season" in requirements.params:
            url = f"{url}/{requirements.params['season']}"
        
        # Build URL based on endpoint type
        if requirements.endpoint == "/api/f1/races":
            if "round" in requirements.params:
                url = f"{url}/{requirements.params['round']}/results"
            else:
                url = f"{url}/results"
                
        elif requirements.endpoint == "/api/f1/qualifying":
            # Get round number
            round_num = None
            if "round" in requirements.params:
                round_num = requirements.params["round"]
            elif "circuit" in requirements.params and "season" in requirements.params:
                circuit_id = self._clean_circuit_name(requirements.params["circuit"])
                if requirements.params["season"] == "2023":
                    round_num = self.circuit_rounds_2023.get(circuit_id)
            
            # Build qualifying URL
            if round_num:
                url = f"{url}/{round_num}/qualifying"
            else:
                url = f"{url}/qualifying"
                
        elif requirements.endpoint == "/api/f1/constructors":
            if "constructor" in requirements.params:
                constructor_id = self._get_constructor_id(requirements.params["constructor"])
                url = f"{url}/constructors/{constructor_id}/results"
                
        elif requirements.endpoint == "/api/f1/drivers":
            if "driver" in requirements.params:
                driver_id = self._get_driver_id(requirements.params["driver"])
                url = f"{url}/drivers/{driver_id}/results"
                
        # Add query parameters
        query_params = []
        if "limit" in requirements.params:
            query_params.append(f"limit={requirements.params['limit']}")
        if "offset" in requirements.params:
            query_params.append(f"offset={requirements.params['offset']}")
            
        if query_params:
            url = f"{url}?{'&'.join(query_params)}"
            
        return url
    
    def _clean_name(self, name: str) -> str:
        """Clean a name to match API format"""
        return name.lower().replace(" ", "_").replace("-", "_")
    
    def _get_driver_id(self, driver: str | list) -> str | list:
        """Get the correct driver ID for the API"""
        if isinstance(driver, list):
            return [self._get_driver_id(d) for d in driver]
        clean_name = self._clean_name(driver)
        return self.driver_ids.get(clean_name, clean_name)
    
    def _get_constructor_id(self, constructor: str) -> str:
        """Get the correct constructor ID for the API"""
        clean_name = self._clean_name(constructor)
        return self.constructor_ids.get(clean_name, clean_name)
    
    def _clean_circuit_name(self, circuit: str) -> str:
        """Convert circuit name to API format"""
        circuit_mapping = {
            "monaco": "monaco",
            "silverstone": "silverstone",
            "monza": "monza",
            "spa": "spa",
            "suzuka": "suzuka",
            "melbourne": "albert_park",
            "melbourne_park": "albert_park",
            "albert_park": "albert_park",
            "red_bull_ring": "spielberg",
            "hungaroring": "hungaroring",
            "spa_francorchamps": "spa",
            "yas_marina": "yas_marina",
            "marina_bay": "marina_bay",
            "americas": "austin",
            "interlagos": "interlagos",
            "mexico": "mexico_city"
        }
        clean_name = self._clean_name(circuit)
        return circuit_mapping.get(clean_name, clean_name)

# Test the pipeline
async def main():
    processor = QueryProcessor()
    pipeline = DataPipeline()
    
    # Test queries
    queries = [
        "What are the results of the 2023 Australian Grand Prix?",  # Season and round
        "How did Lewis Hamilton perform in qualifying at Monaco 2023?",  # Driver and circuit specific
        "Show me Red Bull's constructor points for 2023",  # Constructor specific
        "Get the race results for round 3 of the 2023 season",  # Basic round query
        "What was the qualifying order at Silverstone 2023?"  # Circuit specific qualifying
    ]
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        # Get data requirements
        requirements = await processor.process_query(query)
        print("Requirements:", requirements)
        
        # Process through pipeline
        result = await pipeline.process(requirements)
        if result.success:
            print("Success! First 100 chars of data:", str(result.data)[:100])
        else:
            print("Error:", result.error)

if __name__ == "__main__":
    asyncio.run(main()) 