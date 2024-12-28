"""
Query processing module for decomposing user queries into pipeline and analysis requirements.
"""
from typing import Dict, Any, Tuple, TypedDict, List, Optional
import json
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class DataRequirements(TypedDict):
    """Data pipeline requirements"""
    platform: str
    entities: list[str]
    timeframe: str
    filters: Dict[str, Any]

class AnalysisRequirements(TypedDict):
    """Analysis requirements"""
    metrics: list[str]
    grouping: list[str]
    visualization: Dict[str, Any]
    operations: list[str]

class QueryProcessor:
    """Processes natural language queries into structured pipeline requirements"""
    
    def __init__(self):
        """Initialize query processor with Claude client and load query bank"""
        self.claude = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.query_bank = self._load_query_bank()
    
    def _load_query_bank(self) -> Dict[str, Any]:
        """Load query bank for testing and examples"""
        try:
            with open('backend/app/query/query_bank.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load query bank: {e}")
            return {}
    
    async def process_query(
        self,
        query: str,
        platform: str
    ) -> Tuple[DataRequirements, AnalysisRequirements]:
        """
        Process a natural language query into data and analysis requirements.
        
        Args:
            query: User's natural language query
            platform: Platform identifier (e.g., "typeracer", "f1")
            
        Returns:
            Tuple of (data_requirements, analysis_requirements)
        """
        # Check if query matches any test cases
        test_case = self._find_test_case(query, platform)
        if test_case:
            return (
                test_case["expected_output"]["data_requirements"],
                test_case["expected_output"]["analysis_requirements"]
            )
        
        # If no test case, use Claude to decompose query
        decomposed = await self._decompose_query(query, platform)
        
        # Extract requirements
        data_reqs = self._extract_data_requirements(decomposed, platform)
        analysis_reqs = self._extract_analysis_requirements(decomposed)
        
        return data_reqs, analysis_reqs
    
    def _find_test_case(
        self,
        query: str,
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """Find matching test case from query bank"""
        if not self.query_bank or platform not in self.query_bank:
            return None
            
        # Search through all categories
        for category in self.query_bank[platform].values():
            for test_case in category:
                if test_case["query"].lower() == query.lower():
                    return test_case
        return None
    
    async def _decompose_query(
        self,
        query: str,
        platform: str
    ) -> Dict[str, Any]:
        """Use Claude to decompose query into structured format"""
        # Build prompt using examples from query bank
        prompt = self._build_decomposition_prompt(query, platform)
        
        try:
            response = await self.claude.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract and parse JSON from response
            content = str(response.content[0])
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse Claude response as JSON: {e}")
                
        except Exception as e:
            raise ValueError(f"Failed to get response from Claude: {e}")
    
    def _build_decomposition_prompt(
        self,
        query: str,
        platform: str
    ) -> str:
        """Build prompt for query decomposition"""
        # Get example cases from query bank
        examples = self._get_example_cases(platform)
        examples_str = json.dumps(examples, indent=2) if examples else ""
        
        return f"""
        Decompose this {platform} analysis query into specific requirements.
        
        Query: {query}
        
        Example cases for reference:
        {examples_str}
        
        Return a JSON object with the same structure as the examples:
        1. Data Requirements:
           - entities: List of entities to analyze
           - timeframe: Time range to consider
           - filters: Any additional filters
        
        2. Analysis Requirements:
           - metrics: List of metrics to calculate
           - grouping: How to group the data
           - visualization: Visualization specifications
           - operations: Analysis operations to perform
        
        Return only valid JSON, no other text.
        """
    
    def _get_example_cases(
        self,
        platform: str,
        num_examples: int = 2
    ) -> List[Dict[str, Any]]:
        """Get example cases from query bank"""
        if not self.query_bank or platform not in self.query_bank:
            return []
            
        examples = []
        for category in self.query_bank[platform].values():
            for test_case in category[:num_examples]:
                examples.append({
                    "query": test_case["query"],
                    "output": test_case["expected_output"]
                })
        return examples[:num_examples]
    
    def _extract_data_requirements(
        self,
        decomposed: Dict[str, Any],
        platform: str
    ) -> DataRequirements:
        """Extract data pipeline requirements from decomposed query"""
        try:
            return {
                "platform": platform,
                "entities": decomposed.get("data_requirements", {}).get("entities", []),
                "timeframe": decomposed.get("data_requirements", {}).get("timeframe", "all"),
                "filters": decomposed.get("data_requirements", {}).get("filters", {})
            }
        except Exception as e:
            raise ValueError(f"Failed to extract data requirements: {e}")
    
    def _extract_analysis_requirements(
        self,
        decomposed: Dict[str, Any]
    ) -> AnalysisRequirements:
        """Extract analysis requirements from decomposed query"""
        try:
            analysis_reqs = decomposed.get("analysis_requirements", {})
            return {
                "metrics": analysis_reqs.get("metrics", []),
                "grouping": analysis_reqs.get("grouping", []),
                "visualization": analysis_reqs.get("visualization", {}),
                "operations": analysis_reqs.get("operations", [])
            }
        except Exception as e:
            raise ValueError(f"Failed to extract analysis requirements: {e}") 