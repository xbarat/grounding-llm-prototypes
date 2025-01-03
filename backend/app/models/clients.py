from typing import Dict, Type
from .base import BaseQueryModel, BaseGenerationModel, BaseAssistantModel
from .wrapper import QueryModelWrapper, GenerationModelWrapper, AssistantModelWrapper

class ModelClientFactory:
    _query_models: Dict[str, Type[BaseQueryModel]] = {}
    _generation_models: Dict[str, Type[BaseGenerationModel]] = {}
    _assistant_models: Dict[str, Type[BaseAssistantModel]] = {}

    @classmethod
    def register_query_model(cls, name: str, model_class: Type[BaseQueryModel]):
        cls._query_models[name] = model_class

    @classmethod
    def register_generation_model(cls, name: str, model_class: Type[BaseGenerationModel]):
        cls._generation_models[name] = model_class

    @classmethod
    def register_assistant_model(cls, name: str, model_class: Type[BaseAssistantModel]):
        cls._assistant_models[name] = model_class

    @classmethod
    def create_query_model(cls, name: str, **kwargs) -> BaseQueryModel:
        model = cls._query_models[name](**kwargs)
        return QueryModelWrapper(model)

    @classmethod
    def create_generation_model(cls, name: str, **kwargs) -> BaseGenerationModel:
        model = cls._generation_models[name](**kwargs)
        return GenerationModelWrapper(model)

    @classmethod
    def create_assistant_model(cls, name: str, **kwargs) -> BaseAssistantModel:
        model = cls._assistant_models[name](**kwargs)
        return AssistantModelWrapper(model) 