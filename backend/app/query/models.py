"""Shared data models for query processing"""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class DataRequirements:
    """Requirements for fetching F1 data"""
    endpoint: str  # The F1 API endpoint to query
    params: Dict[str, Any]  # Parameters for the API call

@dataclass
class ProcessingResult:
    """Enhanced result structure for comparison"""
    requirements: DataRequirements
    processing_time: float
    source: str  # 'q2' or 'legacy'
    confidence: float = 0.0
    trace: List[str] = field(default_factory=list) 