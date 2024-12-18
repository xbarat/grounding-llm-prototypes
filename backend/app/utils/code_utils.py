import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Tuple, Optional
from anthropic import Anthropic
import os
from app.utils.prompts import custom_prompt, custom_prompt_with_error
from app.utils.variable_mapper import VariableMapper, preprocess_code

# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def generate_code(df: pd.DataFrame, user_question: str) -> str:
    """Generate code using Claude API"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)    
    prompt = custom_prompt(df, user_question)
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude Response Failed (103): {str(e)}"

def execute_code_safely(code: str, df: pd.DataFrame) -> Tuple[bool, str, str]:
    """Execute code in a safe environment with proper setup"""
    try:
        # Initialize variable mapper and setup
        mapper = VariableMapper(df)
        
        # Create a copy of DataFrame with timestamp
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        
        # Setup execution environment
        local_ns = {
            'pd': pd,
            'df': df,
            'plt': plt,
            'sns': sns,
            'np': np
        }
        
        # Preprocess code
        modified_code, _ = preprocess_code(code, mapper)
        
        # Execute code
        exec(modified_code, local_ns)
        
        # Handle results
        result = local_ns.get('result', None)
        if plt.get_fignums():
            plt.close()
            
        return True, str(result) if result is not None else "", modified_code
        
    except Exception as e:
        return False, str(e), code

class QueryGuidance:
    def filter_questions(self) -> list:
        """Return a list of suggested questions"""
        return [
            "What is my average typing speed?",
            "Show my speed trend over time",
            "What is my fastest race?",
            "What is my accuracy trend?",
            "How many races have I completed?"
        ] 