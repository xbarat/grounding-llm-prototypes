"""
Q2 Assistants - Enhanced Query Processing System
This module implements the first phase of the multi-agent query processing system.
Q2 refers to the "Query Quality" improvement initiative.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Pattern
import json
import logging
import time
import re
from functools import lru_cache
from openai import AsyncOpenAI
from .models import DataRequirements

# Configure logging for Q2 system
logger = logging.getLogger("q2_assistants")

# Common query patterns for quick matching
QUERY_PATTERNS = {
    # Performance patterns
    r"(?i)(how|what|show).*(performance|results?).*(?P<driver>\w+\s+\w+).*(?P<year>\d{4})": {
        "action": "fetch",
        "entity": "drivers",
        "template": lambda m: {
            "driver": m.group("driver").lower().replace(" ", "_"),
            "season": m.group("year")
        }
    },
    # Comparison patterns
    r"(?i)compare.*(?P<item1>\w+\s+\w+).*(?P<item2>\w+\s+\w+)": {
        "action": "compare",
        "entity": "drivers",
        "template": lambda m: {
            "driver": [
                m.group("item1").lower().replace(" ", "_"),
                m.group("item2").lower().replace(" ", "_")
            ]
        }
    },
    # Historical patterns with statistics
    r"(?i)(since|from)\s+(?P<year>\d{4}).*(?P<stat>win\s+rate|podiums?|points?).*(?P<team>\w+)": {
        "action": "analyze",
        "entity": "standings/constructors",  # Changed to standings for statistical analysis
        "template": lambda m: {
            "season": list(map(str, range(int(m.group("year")), 2024))),
            "constructor": m.group("team").lower().replace(" ", "_")
        }
    },
    # Simple historical patterns
    r"(?i)(since|from)\s+(?P<year>\d{4})": {
        "action": "analyze",
        "entity": "constructors",
        "template": lambda m: {
            "season": list(map(str, range(int(m.group("year")), 2024)))
        }
    }
}

@dataclass
class Q2Parameters:
    """
    Enhanced parameter structure for Q2 system
    Extends the basic query understanding with action-based processing
    """
    action: str  # Type of action: rank, compare, fetch, analyze
    entity: str  # Target entity: driver, constructor, race, qualifying
    parameters: Dict[str, Any]  # Extracted parameters
    confidence: float = 0.0  # Confidence score of the parsing

@dataclass
class Q2Result:
    """
    Q2 processing result with metadata for analysis
    Used to track and compare performance with legacy system
    """
    requirements: DataRequirements
    confidence: float
    processing_time: float
    agent_trace: List[str] = field(default_factory=list)  # Initialize as empty list

class UnderstandingAgent:
    """
    Q2 Agent 1: Query Understanding and Parameter Recognition
    Focuses on extracting structured information from natural language
    """
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.pattern_cache = {}
        
    @lru_cache(maxsize=100)
    def _match_common_pattern(self, query: str) -> Optional[Tuple[Q2Parameters, List[str]]]:
        """Try to match query against common patterns first"""
        for pattern, config in QUERY_PATTERNS.items():
            match = re.match(pattern, query)
            if match:
                params = config["template"](match)
                return Q2Parameters(
                    action=config["action"],
                    entity=config["entity"],
                    parameters=params,
                    confidence=0.9  # High confidence for pattern matches
                ), ["Matched common query pattern"]
        return None

    async def parse_query(self, query: str) -> Tuple[Q2Parameters, List[str]]:
        """
        Parse natural language query into structured parameters
        Returns both parameters and reasoning trace
        """
        # Q2 Enhancement: Detailed prompt for better parameter extraction
        prompt = f"""You are an expert query parser for F1 data. Extract structured parameters from this query and return a JSON response.
        Focus on identifying:
        1. Primary action (rank, compare, fetch, analyze)
        2. Target entity (driver, constructor, race, qualifying)
        3. Specific parameters (season, driver, constructor, circuit)
        4. Temporal aspects (specific dates, ranges, 'last N races')

        Query: {query}

        Return a JSON response in this exact format:
        {{
            "action": string,
            "entity": string,
            "parameters": {{
                "season": string | string[],
                "driver": string | string[],
                "constructor": string,
                "circuit": string,
                "round": string
            }},
            "reasoning": string[]
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            confidence = self._calculate_confidence(parsed)
            
            return Q2Parameters(
                action=parsed["action"],
                entity=parsed["entity"],
                parameters=parsed["parameters"],
                confidence=confidence
            ), parsed.get("reasoning", [])
            
        except Exception as e:
            logger.error(f"Q2 Understanding Agent error: {str(e)}")
            raise

    def _calculate_confidence(self, parsed: Dict) -> float:
        """Q2: Calculate confidence score based on parameter completeness"""
        required_fields = {"action", "entity", "parameters"}
        optional_params = {"season", "driver", "constructor", "circuit", "round"}
        
        # Check required fields
        base_score = sum(1 for field in required_fields if field in parsed) / len(required_fields)
        
        # Check parameter completeness
        param_score = sum(1 for param in optional_params if param in parsed.get("parameters", {})) / len(optional_params)
        
        return (base_score * 0.6 + param_score * 0.4)  # Weighted average

class EndpointMappingAgent:
    """
    Q2 Agent 2: Endpoint Mapping
    Maps parsed parameters to specific API endpoints
    """
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.endpoint_patterns = {
            # Enhanced pattern matching with more specific patterns
            ("rank", "drivers"): ("/api/f1/standings/drivers", lambda p: p),
            ("rank", "constructors"): ("/api/f1/standings/constructors", lambda p: p),
            ("compare", "drivers"): ("/api/f1/drivers", lambda p: {"driver": p.get("drivers", [])}),
            ("analyze", "laps"): ("/api/f1/laps", lambda p: p),
            ("analyze", "qualifying"): ("/api/f1/qualifying", lambda p: p),
            ("analyze", "standings/constructors"): ("/api/f1/standings/constructors", lambda p: p),  # For statistical analysis
            ("analyze", "constructors"): ("/api/f1/constructors", lambda p: p),  # For raw results
            ("fetch", "race"): ("/api/f1/results", lambda p: p),
            ("fetch", "drivers"): ("/api/f1/drivers", lambda p: p),
        }
        
    @lru_cache(maxsize=50)
    def _get_endpoint_pattern(self, action: str, entity: str) -> Optional[Tuple[str, callable]]:
        """Cached endpoint pattern lookup"""
        return self.endpoint_patterns.get((action, entity))

    def _try_pattern_match(self, params: Q2Parameters) -> Optional[DataRequirements]:
        """Enhanced pattern matching with parameter transformation"""
        pattern_match = self._get_endpoint_pattern(params.action, params.entity)
        if pattern_match:
            endpoint, transform = pattern_match
            return DataRequirements(
                endpoint=endpoint,
                params=transform(params.parameters)
            )
        return None

    async def map_to_endpoint(self, params: Q2Parameters) -> Tuple[DataRequirements, List[str]]:
        """
        Map Q2Parameters to specific API endpoint
        Returns both requirements and reasoning trace
        """
        try:
            # Try pattern matching first
            pattern_result = self._try_pattern_match(params)
            if pattern_result:
                return pattern_result, ["Pattern matched endpoint found"]
            
            # Fallback to AI mapping
            prompt = f"""Map these F1 query parameters to the correct API endpoint and return a JSON response.
            Parameters: {json.dumps(params.__dict__)}
            
            Available endpoints:
            - /api/f1/races: Race results for a season
            - /api/f1/qualifying: Qualifying results
            - /api/f1/drivers: Results for specific drivers
            - /api/f1/constructors: Results for constructors
            - /api/f1/laps: Lap times
            - /api/f1/standings/drivers: Driver standings
            - /api/f1/standings/constructors: Constructor standings
            
            Return a JSON response as:
            {{
                "endpoint": string,
                "modified_params": object,
                "reasoning": string[]
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            parsed = json.loads(response.choices[0].message.content)
            
            return DataRequirements(
                endpoint=parsed["endpoint"],
                params=parsed["modified_params"]
            ), parsed.get("reasoning", [])
            
        except Exception as e:
            logger.error(f"Q2 Endpoint Mapping error: {str(e)}")
            raise

class Q2Processor:
    """
    Main Q2 processing coordinator
    Manages the multi-agent workflow and comparison with legacy system
    """
    
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.understanding_agent = UnderstandingAgent(client)
        self.mapping_agent = EndpointMappingAgent(client)
        
    async def process_query(self, query: str) -> Q2Result:
        """
        Process query using Q2 multi-agent system
        Returns enhanced result with confidence and tracing
        """
        trace = []
        try:
            # Step 1: Query Understanding
            params, understanding_trace = await self.understanding_agent.parse_query(query)
            trace.extend(["Understanding Phase:"] + understanding_trace)
            
            # Step 2: Endpoint Mapping
            requirements, mapping_trace = await self.mapping_agent.map_to_endpoint(params)
            trace.extend(["Mapping Phase:"] + mapping_trace)
            
            # Q2: Calculate overall confidence
            confidence = params.confidence * 0.7 + (1.0 if requirements else 0.0) * 0.3
            
            return Q2Result(
                requirements=requirements,
                confidence=confidence,
                processing_time=0.0,  # TODO: Add timing
                agent_trace=trace
            )
            
        except Exception as e:
            logger.error(f"Q2 Processing error: {str(e)}")
            raise 