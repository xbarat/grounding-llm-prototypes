# Overview

1. **File Structure Changes**
backend/app/
├── models/                    # Central models directory
│   ├── __init__.py
│   ├── base.py               # Base interfaces
│   ├── gpt4_mini.py          # Query understanding model
│   ├── claude.py             # Code generation model
│   ├── gpt4.py              # Code generation model
│   ├── gpt4_assistant.py     # Direct analysis model
│   └── clients.py            # Model client factory
├── analyst/
│   ├── __init__.py
│   ├── assistants.py         # Model registry & configuration
│   ├── pipeline.py           # Pipeline orchestration
│   ├── prompts.py           # Existing prompts file
│   ├── generate.py          # Existing generation logic
│   └── config/
│       └── models.yaml       # Model configuration
└── pipeline/                 # Existing data pipeline
    └── data2.py             # Existing data fetching

2. **Implementation Plan**

a. **Step 1: Base Interfaces**
```python
# models/base.py
class BaseQueryModel:
    async def query_understanding(self, query: str) -> DataRequirements:
        raise NotImplementedError

class BaseGenerationModel:
    async def code_generation(self, df: pd.DataFrame, requirements: DataRequirements) -> str:
        raise NotImplementedError

class BaseAssistantModel:
    async def direct_analysis(self, context: dict) -> AnalysisResult:
        raise NotImplementedError
```

b. **Step 2: Model Registry**
```python
# assistants.py
from .models import GPT4Mini, ClaudeModel, GPT4Model, GPT4Assistant

MODEL_REGISTRY = {
    "query": {
        "gpt4-mini": GPT4Mini(),
    },
    "generation": {
        "claude": ClaudeModel(),
        "gpt4": GPT4Model(),
    },
    "assistant": {
        "gpt4-assistant": GPT4Assistant(),
    }
}
```

c. **Step 3: Simple Pipeline**
```python
# pipeline.py
class AnalysisPipeline:
    def __init__(self, config: dict):
        self.query_model = MODEL_REGISTRY["query"][config["query_model"]]
        self.generation_model = MODEL_REGISTRY["generation"][config["generation_model"]]
        self.assistant_model = MODEL_REGISTRY["assistant"][config["assistant_model"]]
        self.logger = setup_logger()

    async def process(self, query: str) -> AnalysisResult:
        try:
            # Log start time
            start = time.time()
            
            # Query understanding
            requirements = await self.query_model.query_understanding(query)
            self.logger.info(f"Query processed in {time.time() - start}s")

            # Data fetching (existing pipeline)
            data = await fetch_data(requirements)

            # Choose analysis path
            if self.should_use_assistant(requirements):
                result = await self.assistant_model.direct_analysis({
                    "query": query,
                    "data": data
                })
            else:
                code = await self.generation_model.code_generation(data, requirements)
                result = await execute_code(code)

            return result

        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}")
            raise
```

3. **Minimal Metrics Implementation**
```python
# metrics.py
class MetricsLogger:
    def __init__(self):
        self.metrics = defaultdict(list)

    def log_latency(self, model: str, operation: str, duration: float):
        self.metrics[f"{model}_{operation}_latency"].append(duration)

    def log_success(self, model: str, operation: str, success: bool):
        self.metrics[f"{model}_{operation}_success"].append(success)

    def get_summary(self) -> dict:
        return {
            k: {
                "mean": np.mean(v),
                "count": len(v),
                "success_rate": np.mean(v) if "success" in k else None
            }
            for k, v in self.metrics.items()
        }
```

4. **Configuration**
```yaml
# config/models.yaml
default:
  query_model: gpt4-mini
  generation_model: claude
  assistant_model: gpt4-assistant

experimental:
  query_model: gpt4-mini
  generation_model: gpt4
  assistant_model: gpt4-assistant
```

Key Features:
1. Simple model switching through configuration
2. Basic metrics collection
3. Clear separation of model implementations
4. Minimal error handling with logging
5. Easy to extend with new models

