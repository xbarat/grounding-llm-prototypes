"""Code generation and execution module"""
import os
import re
import sys
import traceback
from io import StringIO
from contextlib import redirect_stdout
from typing import Tuple, Dict, Any, Optional, Union, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from anthropic import Anthropic
from .prompts import f1_prompt, stable_prompt_with_error, custom_prompt
import io
import base64
import numpy as np
from .variable_mapper import VariableMapper, preprocess_code

# Load environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def generate_code(df: pd.DataFrame, query: str) -> str:
    """Generate analysis code using Claude"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Generate prompt using F1-specific visualization prompt
    prompt = f1_prompt(df, query)
    
    # Get response from Claude
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract the text content from the response
    content = str(response.content)
    return content

def extract_code_block(response: str) -> Optional[str]:
    """Extract Python code block from Claude's response"""
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, response, re.DOTALL)
    if not matches:
        return None
        
    # Clean up the code block
    code = matches[0]
    code = code.replace('\\n', '\n')  # Convert escaped newlines
    code = code.replace("\\'", "'")   # Convert escaped quotes
    code = code.strip()
    return code

def execute_code_safely(code: str, data: pd.DataFrame) -> Tuple[bool, Dict[str, Any], str]:
    """Execute generated code in a safe environment"""
    try:
        # Print the code being executed for debugging
        print("\nExecuting code:")
        print(code)
        
        # Create variable mapper and preprocess code
        mapper = VariableMapper(data)
        modified_code, used_mappings = preprocess_code(code, mapper)
        
        print("\nPreprocessed code:")
        print(modified_code)
        
        # Create a new globals dict with limited access
        globals_dict = {
            'pd': pd,
            'plt': plt,
            'np': np,
            'data': data.copy(),  # Use a copy to prevent modifications to original
            'df': data.copy(),    # Add df reference since some code might use it
            'print': print,
            'sns': sns
        }
        
        # Validate data
        if data is None or len(data) == 0:
            return False, {
                "success": False,
                "error": "No data available for visualization"
            }, modified_code
        
        # Convert season to numeric if it exists
        if 'season' in data.columns:
            try:
                globals_dict['data']['season'] = pd.to_numeric(globals_dict['data']['season'])
                globals_dict['df']['season'] = pd.to_numeric(globals_dict['df']['season'])
                print("\nConverted season to numeric successfully")
            except Exception as e:
                print(f"\nError converting season to numeric: {str(e)}")
                
        # Convert round to numeric if it exists
        if 'round' in data.columns:
            try:
                globals_dict['data']['round'] = pd.to_numeric(globals_dict['data']['round'])
                globals_dict['df']['round'] = pd.to_numeric(globals_dict['df']['round'])
                print("\nConverted round to numeric successfully")
            except Exception as e:
                print(f"\nError converting round to numeric: {str(e)}")
            
        # Print data types for debugging
        print("\nData Types Before Execution:")
        print(globals_dict['data'].dtypes)
            
        # Execute the preprocessed code
        exec(modified_code, globals_dict)
        
        # Get the figure from globals
        fig = plt.gcf()
        
        # Convert plot to base64 string
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Get printed output
        output = globals_dict.get('output', '')
        
        # Ensure we have a visualization
        if not image_base64:
            return False, {
                "success": False,
                "error": "No visualization was generated"
            }, modified_code
        
        return True, {
            "success": True,
            "output": output,
            "figure": image_base64,
            "data": globals_dict['data'].to_dict('records') if isinstance(globals_dict['data'], pd.DataFrame) else globals_dict['data']
        }, modified_code
        
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}\n{traceback.format_exc()}"
        print("\nError Details:")
        print(error_msg)
        print("\nData shape:", data.shape)
        print("\nData columns:", data.columns.tolist())
        print("\nData sample:", data.head())
        return False, {
            "success": False,
            "error": error_msg
        }, code

def regenerate_code_with_error(df: pd.DataFrame, question: str, error_message: str, previous_code: str) -> str:
    """Regenerate code after an error"""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Use error-specific prompt
    prompt = stable_prompt_with_error(df, question, error_message, previous_code)
    
    # Get new response from Claude
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract the text content from the response
    content = str(response.content)
    return content 