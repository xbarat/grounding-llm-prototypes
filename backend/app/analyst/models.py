"""Model implementations for code generation"""
import os
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
from anthropic import Anthropic
from openai import OpenAI

class CodeGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate code from prompt"""
        pass

class ClaudeCodeGenerator(CodeGenerator):
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-3-sonnet-20240229"
    
    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        return str(response.content)

class GPT4CodeGenerator(CodeGenerator):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-2024-08-06"
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1500
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("GPT-4 returned None response")
        return content

def get_code_generator(model_name: str = "claude") -> CodeGenerator:
    """Factory function to get the appropriate code generator"""
    generators = {
        "claude": ClaudeCodeGenerator,
        "gpt4": GPT4CodeGenerator
    }
    
    generator_class = generators.get(model_name.lower())
    if not generator_class:
        raise ValueError(f"Unknown model: {model_name}. Available models: {list(generators.keys())}")
    
    return generator_class() 