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
import io
import base64
import numpy as np
from .variable_mapper import VariableMapper, preprocess_code
from .models import get_code_generator
import logging
from .prompts import f1_prompt

logger = logging.getLogger(__name__)

def generate_code(data: Union[pd.DataFrame, Dict[str, Any]], query: str, is_follow_up: bool = False) -> str:
    """Generate Python code for F1 data analysis based on the query"""
    try:
        # Convert data to DataFrame if it's a dictionary
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data

        # Get code generator
        generator = get_code_generator("gpt4")

        # Add follow-up context to the prompt if needed
        follow_up_context = """
This is a follow-up query to a previous analysis. The data provided is from the previous query's results.
Focus on answering the specific follow-up question using the existing data.
"""

        # Generate base prompt
        prompt = f1_prompt(df, query)
        
        # Add follow-up context if needed
        if is_follow_up:
            prompt += follow_up_context

        # Get response from model
        content = generator.generate(prompt)
        return content
        
    except Exception as e:
        logger.exception("Error generating code")
        return ""

def extract_code_block(response: str) -> Optional[str]:
    """Extract Python code block from model's response"""
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
            'sns': sns,
            'io': io,
            'base64': base64
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
            
        # Modify the code to capture the figure before plt.show()
        capture_code = """
# Get the current figure
fig = plt.gcf()

# Save to buffer
buffer = io.BytesIO()
fig.savefig(buffer, format='png', bbox_inches='tight')
buffer.seek(0)
captured_figure = base64.b64encode(buffer.getvalue()).decode()
"""
        
        # Insert capture code before any plt.show()
        if "plt.show()" in modified_code:
            modified_code = modified_code.replace("plt.show()", capture_code + "\nplt.show()")
        else:
            modified_code = modified_code + "\n" + capture_code
            
        # Execute the modified code
        exec(modified_code, globals_dict)
        
        # Get the captured figure and output
        image_base64 = globals_dict.get('captured_figure', '')
        output = globals_dict.get('output', '')
        
        # Clean up
        plt.close('all')
        
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

def regenerate_code_with_error(df: pd.DataFrame, question: str, error_message: str, previous_code: str, model: str = "claude") -> str:
    """Regenerate code after an error using specified model"""
    generator = get_code_generator(model)
    
    # Use error-specific prompt
    from .prompts import stable_prompt_with_error
    prompt = stable_prompt_with_error(df, question, error_message, previous_code)
    
    # Get response from model
    content = generator.generate(prompt)
    return content 