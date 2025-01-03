from typing import Dict, Any
import yaml
from ..models.clients import ModelClientFactory
from ..models.gpt4_mini import GPT4Mini
from ..models.claude import ClaudeModel
from ..models.gpt4_assistant import GPT4Assistant

def load_config(config_path: str = "config/models.yaml") -> Dict[str, Any]:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def initialize_models(config: Dict[str, Any]):
    # Register models
    ModelClientFactory.register_query_model("gpt4-mini", GPT4Mini)
    ModelClientFactory.register_generation_model("claude", ClaudeModel)
    ModelClientFactory.register_assistant_model("gpt4-assistant", GPT4Assistant)

    # Create instances based on config
    return {
        "query": ModelClientFactory.create_query_model(
            config["query_model"],
            api_key=config.get("api_keys", {}).get("openai")
        ),
        "generation": ModelClientFactory.create_generation_model(
            config["generation_model"],
            api_key=config.get("api_keys", {}).get("anthropic")
        ),
        "assistant": ModelClientFactory.create_assistant_model(
            config["assistant_model"],
            api_key=config.get("api_keys", {}).get("openai")
        )
    } 