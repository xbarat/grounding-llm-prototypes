import os
import re
import time
import json
import asyncio
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import AsyncAnthropic
from pandas import DataFrame

# Local imports
from .code_utils import generate_code
from .f1_api import F1API
from .platform_fetcher import fetch_typeracer_data

class QueryValidationError(Exception):
    """Raised when query validation fails."""
    pass

class QueryProcessor:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.metrics = QueryMetrics()
        self.validator = QueryValidator()
        self.f1_api = F1API()
        
        # Load query templates
        self.templates = QUERY_TEMPLATES
        
        # Initialize system prompt
        self.system_prompt = """
        You are a query processing expert that converts natural language queries 
        about F1 and TypeRacer data into structured API calls and analysis requirements.
        
        Available F1 endpoints:
        - /current/driverStandings.json
        - /drivers/{driverId}/results.json
        - /current/last/results.json
        - /current/last/qualifying.json
        - /circuits/{circuitId}/results.json
        
        Available TypeRacer endpoints:
        - /pit/race_history?n=100&username={username}
        - /text_stats?username={username}
        
        Convert user queries into API calls and analysis requirements.
        """

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query into API calls and analysis requirements."""
        start_time = time.time()
        
        try:
            # Try matching query templates first
            for template_name, template in self.templates.items():
                match = re.match(template["pattern"], query, re.IGNORECASE)
                if match:
                    response = self._process_template_match(template_name, match)
                    if response:
                        return response

            # If no template matches, use Claude
            prompt = self._build_prompt(query)
            response = await self._get_claude_response(prompt)
            
            # Validate response
            self.validator.validate_query_response(response)
            
            # Record metrics
            self.metrics.record_metric(
                "query_processing_time", 
                time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            self.metrics.record_metric(
                "query_processing_errors", 
                {"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            raise

    def _build_prompt(self, query: str) -> str:
        """Build prompt for Claude."""
        return f"""
        {self.system_prompt}
        
        Convert this query into API calls and analysis requirements:
        {query}
        
        Output must be valid JSON with this structure:
        {{
            "api_calls": [
                {{
                    "endpoint": str,
                    "parameters": dict,
                    "required_fields": list[str]
                }}
            ],
            "analysis_requirements": {{
                "metrics": list[str],
                "visualization": str,
                "additional_processing": dict
            }}
        }}
        """

    async def _get_claude_response(self, prompt: str) -> Dict[str, Any]:
        """Get response from Claude and parse it."""
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Get the response content as a string
            content = str(response.content)
            
            # Try to find a JSON object in the response
            try:
                # Look for content between curly braces
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
                
            raise QueryValidationError("Could not find valid JSON in Claude response")
            
        except Exception as e:
            raise QueryValidationError(f"Error processing Claude response: {str(e)}")

    async def _fetch_platform_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from the appropriate platform."""
        if endpoint.startswith('/pit/') or endpoint.startswith('/text_stats'):
            username = params.get('username')
            if not username:
                raise QueryValidationError("Username required for TypeRacer queries")
            return await fetch_typeracer_data(username, endpoint, params)
        else:
            # Map endpoint to F1API methods
            if endpoint == '/current/driverStandings.json':
                return await self.f1_api.fetch_driver_standings()
            elif endpoint.startswith('/drivers/'):
                driver_id = endpoint.split('/')[2].replace('.json', '')
                return await self.f1_api.fetch_driver_results(driver_id)
            elif endpoint == '/current/last/results.json':
                return await self.f1_api.fetch_race_results()
            elif endpoint == '/current/last/qualifying.json':
                return await self.f1_api.fetch_qualifying_results()
            elif endpoint.startswith('/circuits/'):
                circuit_id = endpoint.split('/')[2].replace('.json', '')
                return await self.f1_api.fetch_circuit_results(circuit_id)
            else:
                raise QueryValidationError(f"Unsupported F1 endpoint: {endpoint}")

    async def execute_query(self, query_response: Dict[str, Any]) -> DataFrame:
        """Execute the API calls from a query response and return a DataFrame."""
        try:
            data = []
            for call in query_response["api_calls"]:
                response = await self._fetch_platform_data(
                    call["endpoint"],
                    call.get("parameters", {})
                )
                data.append(response)
                
            # Create DataFrame from responses
            if len(data) > 1:
                # Merge multiple responses
                combined_data = {}
                for d in data:
                    combined_data.update(d)
                df = DataFrame(combined_data)
            else:
                df = DataFrame(data[0])
                
            # Apply transformations if needed
            if query_response["analysis_requirements"].get("additional_processing"):
                df = self._apply_transformations(df, query_response["analysis_requirements"]["additional_processing"])
                
            return df
            
        except Exception as e:
            raise QueryValidationError(f"Error executing query: {str(e)}")

    def _apply_transformations(self, df: DataFrame, processing: Dict[str, Any]) -> DataFrame:
        """Apply transformations to the DataFrame."""
        try:
            if processing.get("time_conversion"):
                # Convert time strings to datetime
                time_columns = df.select_dtypes(include=['object']).columns
                for col in time_columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        continue
                        
            if processing.get("moving_average"):
                window = processing["moving_average"]
                numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
                for col in numeric_columns:
                    df[f"{col}_ma{window}"] = df[col].rolling(window=window).mean()
                    
            return df
            
        except Exception as e:
            raise QueryValidationError(f"Error applying transformations: {str(e)}")

    def _process_template_match(
        self, 
        template_name: str, 
        match: re.Match
    ) -> Optional[Dict[str, Any]]:
        """Process a template match into a query response."""
        template = self.templates[template_name]
        api_template = template["api_template"]
        
        # Extract parameters from match
        params = match.groupdict()
        
        # Build API calls
        if isinstance(api_template["endpoint"], list):
            api_calls = [
                {
                    "endpoint": endpoint.format(**params),
                    "parameters": api_template.get("parameters", {}),
                    "required_fields": api_template.get("required_fields", [])
                }
                for endpoint in api_template["endpoint"]
            ]
        else:
            api_calls = [{
                "endpoint": api_template["endpoint"].format(**params),
                "parameters": api_template.get("parameters", {}),
                "required_fields": api_template.get("required_fields", [])
            }]

        return {
            "api_calls": api_calls,
            "analysis_requirements": template.get("analysis_requirements", {
                "metrics": [],
                "visualization": "line_chart",
                "additional_processing": {}
            })
        }

class QueryResponse:
    def __init__(self, api_calls: List[Dict], analysis_reqs: Dict):
        self.api_calls = api_calls
        self.analysis_requirements = analysis_reqs
        self.metrics = QueryMetrics()

    async def execute(self) -> DataFrame:
        """Execute API calls and create DataFrame."""
        start_time = time.time()
        
        try:
            data = []
            for call in self.api_calls:
                response = await fetch_platform_data(
                    endpoint=call["endpoint"],
                    params=call["parameters"]
                )
                data.append(response)
                
            df = self._create_dataframe(data)
            
            self.metrics.record_metric(
                "api_call_time",
                time.time() - start_time
            )
            
            return df
            
        except Exception as e:
            self.metrics.record_metric(
                "api_call_errors",
                {"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            raise

    def _create_dataframe(self, data: List[Dict]) -> DataFrame:
        """Convert API responses to analysis-ready DataFrame."""
        # Combine multiple responses if needed
        if len(data) > 1:
            # Merge data based on common fields
            combined_data = self._merge_responses(data)
        else:
            combined_data = data[0]
            
        # Convert to DataFrame
        df = DataFrame(combined_data)
        
        # Apply any required transformations
        if self.analysis_requirements.get("additional_processing"):
            df = self._apply_transformations(df)
            
        return df

    def _merge_responses(self, data: List[Dict]) -> Dict:
        """Merge multiple API responses."""
        # Implementation depends on data structure
        # This is a simple example
        merged = {}
        for d in data:
            merged.update(d)
        return merged

    def _apply_transformations(self, df: DataFrame) -> DataFrame:
        """Apply transformations specified in analysis requirements."""
        processing = self.analysis_requirements["additional_processing"]
        
        if processing.get("time_conversion"):
            # Convert time strings to datetime
            time_columns = df.select_dtypes(include=['object']).columns
            for col in time_columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    continue
                    
        if processing.get("moving_average"):
            window = processing["moving_average"]
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                df[f"{col}_ma{window}"] = df[col].rolling(window=window).mean()
                
        return df

class QueryValidator:
    def validate_query_response(self, response: Dict) -> bool:
        """Validate the structure of a query response."""
        required_fields = ["api_calls", "analysis_requirements"]
        if not all(field in response for field in required_fields):
            raise QueryValidationError("Missing required fields in response")
        
        for call in response["api_calls"]:
            if not self._validate_api_call(call):
                raise QueryValidationError(f"Invalid API call: {call}")
        
        if not self._validate_analysis_requirements(response["analysis_requirements"]):
            raise QueryValidationError("Invalid analysis requirements")
        
        return True

    def _validate_api_call(self, call: Dict) -> bool:
        """Validate an individual API call."""
        required_fields = ["endpoint", "parameters", "required_fields"]
        return all(field in call for field in required_fields)

    def _validate_analysis_requirements(self, reqs: Dict) -> bool:
        """Validate analysis requirements."""
        required_fields = ["metrics", "visualization", "additional_processing"]
        return all(field in reqs for field in required_fields)

class QueryMetrics:
    def __init__(self):
        self.metrics = {
            "query_processing_time": [],
            "api_call_time": [],
            "analysis_time": [],
            "query_processing_errors": [],
            "api_call_errors": []
        }

    def record_metric(self, metric_name: str, value: Any):
        """Record a metric value."""
        self.metrics[metric_name].append(value)

    def get_average(self, metric_name: str) -> float:
        """Get average value for a metric."""
        values = [v for v in self.metrics[metric_name] if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0.0

    def get_error_count(self, metric_name: str) -> int:
        """Get count of errors for a metric."""
        return len(self.metrics[metric_name])

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "processing_time_avg": self.get_average("query_processing_time"),
            "api_call_time_avg": self.get_average("api_call_time"),
            "analysis_time_avg": self.get_average("analysis_time"),
            "processing_errors": self.get_error_count("query_processing_errors"),
            "api_call_errors": self.get_error_count("api_call_errors")
        }

# Query templates for common patterns
QUERY_TEMPLATES = {
    "driver_performance": {
        "pattern": r"(.*performance.*|.*results.*|.*stats.*) (for|of) (?P<driver>.*)",
        "api_template": {
            "endpoint": "/drivers/{driver}/results.json",
            "required_fields": ["position", "points", "grid"],
            "analysis_requirements": {
                "metrics": ["position", "points"],
                "visualization": "line_chart",
                "additional_processing": {
                    "trend_analysis": True
                }
            }
        }
    },
    "race_comparison": {
        "pattern": r"compare (?P<driver1>.*) and (?P<driver2>.*)",
        "api_template": {
            "endpoint": [
                "/drivers/{driver1}/results.json",
                "/drivers/{driver2}/results.json"
            ],
            "analysis_requirements": {
                "metrics": ["position", "points"],
                "visualization": "dual_line_chart",
                "additional_processing": {
                    "head_to_head": True
                }
            }
        }
    },
    "qualifying_performance": {
        "pattern": r"qualifying (performance|results) (for|of) (?P<driver>.*)",
        "api_template": {
            "endpoint": "/drivers/{driver}/qualifying.json",
            "parameters": {"season": "current"},
            "required_fields": ["Q1", "Q2", "Q3", "position"],
            "analysis_requirements": {
                "metrics": ["Q3_time", "position"],
                "visualization": "scatter_plot",
                "additional_processing": {
                    "time_conversion": True
                }
            }
        }
    },
    "typeracer_trend": {
        "pattern": r"(typing|speed|accuracy) (trend|history|progress) for (?P<username>.*)",
        "api_template": {
            "endpoint": "/pit/race_history",
            "parameters": {"n": 100},
            "required_fields": ["wpm", "accuracy"],
            "analysis_requirements": {
                "metrics": ["wpm", "accuracy"],
                "visualization": "line_chart",
                "additional_processing": {
                    "moving_average": 5
                }
            }
        }
    }
} 