from typing import Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class DataRequirements:
    fields: list[str]
    filters: Dict[str, Any]
    time_range: tuple[str, str]

@dataclass
class AnalysisResult:
    data: Any
    explanation: str
    code: Optional[str] = None

class BaseQueryModel:
    async def query_understanding(self, query: str) -> DataRequirements:
        raise NotImplementedError

class BaseGenerationModel:
    async def code_generation(self, df: pd.DataFrame, requirements: DataRequirements) -> str:
        raise NotImplementedError

class BaseAssistantModel:
    async def direct_analysis(self, context: dict) -> AnalysisResult:
        raise NotImplementedError 