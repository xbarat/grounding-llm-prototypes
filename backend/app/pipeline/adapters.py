"""
Adapters for Q2 Pipeline System
Handles conversions between different data types and formats in the pipeline.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union
from ..query.processor import ProcessingResult
from ..query.models import DataRequirements

@dataclass
class AdaptedQueryResult:
    """Unified format for query results throughout the pipeline"""
    endpoint: str
    params: Dict[str, Any]
    metadata: Dict[str, Any]
    source_type: str
    
    @classmethod
    def from_processing_result(cls, result: ProcessingResult) -> "AdaptedQueryResult":
        """Convert ProcessingResult to AdaptedQueryResult"""
        return cls(
            endpoint=result.requirements.endpoint,
            params=result.requirements.params,
            metadata={
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "source": result.source
            },
            source_type="processing_result"
        )
    
    def to_data_requirements(self) -> DataRequirements:
        """Convert to DataRequirements for pipeline processing"""
        return DataRequirements(
            endpoint=self.endpoint,
            params=self.params
        )

class QueryResultAdapter:
    """Adapter for query processing results"""
    
    @staticmethod
    def adapt(result: Union[ProcessingResult, Dict[str, Any]]) -> AdaptedQueryResult:
        """Adapt various input types to unified format"""
        if isinstance(result, ProcessingResult):
            return AdaptedQueryResult.from_processing_result(result)
        elif isinstance(result, dict):
            return AdaptedQueryResult(
                endpoint=result.get("endpoint", ""),
                params=result.get("params", {}),
                metadata=result.get("metadata", {}),
                source_type="dict"
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")
    
    @staticmethod
    def to_pipeline_format(result: AdaptedQueryResult) -> DataRequirements:
        """Convert adapted result to pipeline-compatible format"""
        return result.to_data_requirements()

@dataclass
class PipelineResult:
    """Unified format for pipeline processing results"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Dict[str, Any]
    
    @classmethod
    def from_success(cls, data: Dict[str, Any], metadata: Dict[str, Any]) -> "PipelineResult":
        return cls(
            success=True,
            data=data,
            error=None,
            metadata=metadata
        )
    
    @classmethod
    def from_error(cls, error: str, metadata: Dict[str, Any]) -> "PipelineResult":
        return cls(
            success=False,
            data=None,
            error=error,
            metadata=metadata
        )

class ResultAdapter:
    """Adapter for pipeline results"""
    
    @staticmethod
    def adapt_pipeline_result(result: Any) -> PipelineResult:
        """Convert pipeline result to unified format"""
        if hasattr(result, "success") and hasattr(result, "data"):
            return PipelineResult(
                success=result.success,
                data=result.data if result.success else None,
                error=result.error if hasattr(result, "error") else None,
                metadata={
                    "source": "pipeline",
                    "timestamp": result.timestamp if hasattr(result, "timestamp") else None
                }
            )
        else:
            raise ValueError(f"Unsupported result type: {type(result)}")

class ValidationAdapter:
    """Adapter for data validation"""
    
    @staticmethod
    def validate_query_result(result: AdaptedQueryResult) -> bool:
        """Validate adapted query result"""
        return all([
            isinstance(result.endpoint, str) and result.endpoint,
            isinstance(result.params, dict),
            isinstance(result.metadata, dict),
            isinstance(result.source_type, str)
        ])
    
    @staticmethod
    def validate_pipeline_result(result: PipelineResult) -> bool:
        """Validate pipeline result"""
        return all([
            isinstance(result.success, bool),
            result.data is None or isinstance(result.data, dict),
            result.error is None or isinstance(result.error, str),
            isinstance(result.metadata, dict)
        ]) 