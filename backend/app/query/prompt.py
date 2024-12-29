from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class AnalysisType(Enum):
    """Types of analysis that can be performed"""
    STATISTICAL = "statistical"  # Basic statistics (mean, median, etc.)
    COMPARISON = "comparison"    # Compare performance between entities
    TREND = "trend"             # Historical trends and patterns
    RANKING = "ranking"         # Rankings and standings
    CUSTOM = "custom"           # Custom analysis

@dataclass
class AnalysisConstraints:
    """Constraints for the analysis"""
    time_range: Optional[str] = None          # e.g., "2023", "2023-2024", "last_5_races"
    entities: Optional[List[str]] = None      # e.g., ["lewis_hamilton", "max_verstappen"]
    metrics: Optional[List[str]] = None       # e.g., ["points", "position", "fastest_lap"]
    limit: Optional[int] = None               # Limit the number of results

@dataclass
class AnalysisQuery:
    """Structure for analysis requirements"""
    analysis_type: AnalysisType
    description: str                          # Natural language description of the analysis
    data_context: Dict[str, Any]             # DataFrame structure and available data
    constraints: AnalysisConstraints
    expected_output: str                      # e.g., "table", "graph", "summary"
    
    def to_prompt(self) -> str:
        """Convert analysis query to a prompt for the analysis engine"""
        prompt = f"""Given the following F1 data analysis request:

Analysis Type: {self.analysis_type.value}
Description: {self.description}

Data Context:
{self._format_dict(self.data_context)}

Constraints:
- Time Range: {self.constraints.time_range if self.constraints.time_range else 'Not specified'}
- Entities: {', '.join(self.constraints.entities) if self.constraints.entities else 'Not specified'}
- Metrics: {', '.join(self.constraints.metrics) if self.constraints.metrics else 'Not specified'}
- Limit: {self.constraints.limit if self.constraints.limit else 'Not specified'}

Expected Output: {self.expected_output}

Generate Python code to perform this analysis using pandas and the provided DataFrame.
"""
        return prompt
    
    def _format_dict(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Helper method to format dictionary for prompt"""
        result = []
        for key, value in d.items():
            if isinstance(value, dict):
                result.append("  " * indent + f"{key}:")
                result.append(self._format_dict(value, indent + 1))
            else:
                result.append("  " * indent + f"{key}: {value}")
        return "\n".join(result) 