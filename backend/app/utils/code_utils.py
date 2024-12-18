from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from app.utils.prompts import custom_prompt, custom_prompt_with_error
from app.utils.variable_mapper import VariableMapper, preprocess_code
from app.utils.plotting import setup_plotting_style

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def generate_code(df: pd.DataFrame, user_question: str) -> str:
    """Generate code using Claude API"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Use the custom prompt from prompts.py
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
        raise Exception(f"Code generation failed: {str(e)}")

def extract_code_block(response: str) -> Optional[str]:
    """Extract code block from Claude's response"""
    try:
        start_idx = response.find('```python')
        if start_idx == -1:
            start_idx = response.find('```')
        if start_idx != -1:
            end_idx = response.find('```', start_idx + 3)
            if end_idx != -1:
                code = response[start_idx:end_idx].strip()
                code = code.replace('```python', '').replace('```', '').strip()
                return code
    except Exception as e:
        raise Exception(f"Code extraction failed: {str(e)}")
    return None

def execute_code_safely(code: str, df: pd.DataFrame) -> Tuple[bool, Any, str]:
    """Execute code in a safe environment with proper setup"""
    try:
        # Initialize variable mapper and setup plotting style
        mapper = VariableMapper(df)
        setup_plotting_style()
        
        # Create a copy of DataFrame with timestamp
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        
        # Setup execution environment
        local_ns = {
            'pd': pd,
            'df': df,
            'plt': plt,
            'sns': sns,
            'np': np,
            'result': None
        }
        
        # Preprocess code using variable mapper
        modified_code, _ = preprocess_code(code, mapper)
        
        # Execute code
        exec(modified_code, local_ns)
        
        # Handle results
        result = local_ns.get('result', None)
        figure = None
        
        if plt.get_fignums():
            figure = plt.gcf()
            plt.close()
            
        return True, {'result': result, 'figure': figure}, modified_code
        
    except Exception as e:
        return False, str(e), code

def regenerate_code_with_error(df: pd.DataFrame, question: str, error_message: str, previous_code: str) -> str:
    """Regenerate code with error context using custom prompt"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Use the custom prompt with error from prompts.py
    prompt = custom_prompt_with_error(df, question, error_message, previous_code)
    
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
        return f"Error getting response: {str(e)}"