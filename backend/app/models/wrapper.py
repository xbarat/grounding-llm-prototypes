import time
from typing import Dict, Any, Callable, TypeVar, Awaitable
import pandas as pd
from .base import (
    BaseQueryModel, BaseGenerationModel, BaseAssistantModel,
    DataRequirements, AnalysisResult
)
from .metrics import collector

T = TypeVar('T')

class BaseMetricsWrapper:
    """Base wrapper with common metrics collection logic."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    async def _collect_metrics(self, operation: str, func: Callable[[], Awaitable[T]]) -> T:
        """Helper to collect metrics for any operation."""
        start_time = time.time()
        try:
            result = await func()
            duration = time.time() - start_time
            collector.log_duration(self.model_name, operation, duration)
            collector.log_success(self.model_name, operation, True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            collector.log_duration(self.model_name, operation, duration)
            collector.log_success(self.model_name, operation, False)
            raise e

class QueryModelWrapper(BaseMetricsWrapper, BaseQueryModel):
    """Wrapper for query understanding models."""
    
    def __init__(self, model: BaseQueryModel):
        super().__init__(model.__class__.__name__)
        self.model = model

    async def query_understanding(self, query: str) -> DataRequirements:
        return await self._collect_metrics(
            'query_understanding',
            lambda: self.model.query_understanding(query)
        )

class GenerationModelWrapper(BaseMetricsWrapper, BaseGenerationModel):
    """Wrapper for code generation models."""
    
    def __init__(self, model: BaseGenerationModel):
        super().__init__(model.__class__.__name__)
        self.model = model

    async def code_generation(self, df: pd.DataFrame, requirements: DataRequirements) -> str:
        return await self._collect_metrics(
            'code_generation',
            lambda: self.model.code_generation(df, requirements)
        )

class AssistantModelWrapper(BaseMetricsWrapper, BaseAssistantModel):
    """Wrapper for assistant models."""
    
    def __init__(self, model: BaseAssistantModel):
        super().__init__(model.__class__.__name__)
        self.model = model

    async def direct_analysis(self, context: dict) -> AnalysisResult:
        return await self._collect_metrics(
            'direct_analysis',
            lambda: self.model.direct_analysis(context)
        )

def wrap_model(model: T) -> T:
    """Factory function to wrap a model with appropriate metrics wrapper."""
    if isinstance(model, BaseQueryModel):
        return QueryModelWrapper(model)
    elif isinstance(model, BaseGenerationModel):
        return GenerationModelWrapper(model)
    elif isinstance(model, BaseAssistantModel):
        return AssistantModelWrapper(model)
    raise ValueError(f"Unsupported model type: {type(model)}") 