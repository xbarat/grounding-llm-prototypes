from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from anthropic import AsyncAnthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnalysisEngine:
    """Engine for generating and executing F1 data analysis"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def analyze(self, df: pd.DataFrame, query: str) -> str:
        """Generate and execute analysis based on the query and DataFrame."""
        try:
            # Generate analysis code
            code = await self._generate_code(df, query)
            if not code:
                raise Exception("Failed to generate analysis code")
                
            # Execute the code
            success, result, executed_code = await self._execute_code(code, df)
            if not success:
                raise Exception(f"Code execution failed: {result}")
                
            return result
            
        except Exception as e:
            return f"Analysis error: {str(e)}"

    async def _generate_code(self, df: pd.DataFrame, query: str) -> Optional[str]:
        """Generate analysis code using Claude API"""
        try:
            # Get DataFrame info for the prompt
            df_info = self._get_df_info(df)
            
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""You are an expert Python data analyst. Generate code to analyze Formula 1 qualifying data based on this query: {query}

DataFrame Information:
{df_info}

Requirements:
1. Use pandas for data analysis
2. Include clear comments explaining the code
3. The DataFrame already has timedelta columns for q1, q2, and q3
4. Store the final result in a variable named 'result'
5. Format timedelta values as 'MM:SS.mmm'
6. Include driver names in the output for clarity
7. Format the output with clear sections and spacing
8. Use triple quotes for multiline strings

The code should:
1. Iterate through each row in the DataFrame
2. Extract and format qualifying times (q1, q2, q3) for each driver
3. Format times as MM:SS.mmm using total_seconds() and string formatting
4. Create a formatted string with driver name and their qualifying times
5. Add proper spacing and formatting for readability
6. Calculate and show time differences between drivers

Example time formatting:
```python
def format_time(td):
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"

# Example usage:
q1_formatted = format_time(row['q1'])  # Returns "01:12.386"
```

The code should be complete and executable. Only return the code, no explanations."""
                }]
            )
            
            # Extract code from response
            if response.content:
                content = str(response.content)
                return self._extract_code_block(content)
            return None
            
        except Exception as e:
            print(f"Code generation failed: {str(e)}")
            return None

    async def _execute_code(self, code: str, df: pd.DataFrame) -> Tuple[bool, Any, str]:
        """Execute the generated code safely"""
        try:
            # Setup execution environment
            local_ns = {
                'pd': pd,
                'df': df.copy(),
                'plt': plt,
                'sns': sns,
                'np': np,
                'result': None,
                'print': print  # Allow print statements in the code
            }
            
            # Add globals that might be needed
            global_ns = {
                '__builtins__': __builtins__,
                'pd': pd,
                'plt': plt,
                'sns': sns,
                'np': np
            }
            
            # Execute the code
            exec(code, global_ns, local_ns)
            
            # Get the result
            result = local_ns.get('result', None)
            
            # Handle any plots
            if plt.get_fignums():
                plt.close('all')
            
            return True, result, code
            
        except Exception as e:
            print(f"Code execution error: {str(e)}")
            print("Generated code:")
            print(code)
            return False, str(e), code

    def _extract_code_block(self, content: str) -> Optional[str]:
        """Extract code block from Claude's response"""
        try:
            # Extract code block
            if '```python' in content:
                code = content.split('```python')[1].split('```')[0]
            elif '```' in content:
                code = content.split('```')[1].split('```')[0]
            else:
                # Try to find code in text block format
                if '[TextBlock(text=' in content:
                    code = content.split('[TextBlock(text=')[1]
                    code = code.split("', type='text')]")[0]
                    # Remove the first line if it's a description
                    if code.startswith("'Here's the Python code"):
                        code = code.split('\n\n', 1)[1]
                else:
                    code = content
                
            # Clean up the code
            code = code.strip()
            code = code.replace('\\n', '\n')  # Replace escaped newlines
            code = code.replace('\\"', '"')   # Replace escaped quotes
            code = code.replace("\\'", "'")   # Replace escaped single quotes
            code = code.replace('\\', '')     # Remove remaining backslashes
            
            return code
        except Exception as e:
            print(f"Code extraction failed: {str(e)}")
            return None

    def _get_df_info(self, df: pd.DataFrame) -> str:
        """Get DataFrame information for the prompt"""
        info = []
        info.append(f"Shape: {df.shape}")
        info.append("\nColumns and data types:")
        for col in df.columns:
            info.append(f"- {col}: {df[col].dtype}")
        info.append("\nFirst few rows:")
        info.append(str(df.head()))
        return "\n".join(info) 